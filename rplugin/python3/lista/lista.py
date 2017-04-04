import logging
import time
from threading import Timer
import datetime
import asyncio
import re
from collections import namedtuple
from lista.prompt.prompt import (  # type: ignore
    INSERT_MODE_INSERT,
    Prompt,
)
from .action import DEFAULT_ACTION_KEYMAP, DEFAULT_ACTION_RULES
from .indexer import Indexer
from .matcher.all import Matcher as AllMatcher
from .matcher.fuzzy import Matcher as FuzzyMatcher
from .util import assign_content

logging.basicConfig(filename='/Users/tolgraven/lista.log', level=logging.DEBUG)

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9a-zA-Z;]*?m')

CASE_SMART = 1
CASE_IGNORE = 2
CASE_NORMAL = 3

CASES = (
    CASE_SMART,
    CASE_IGNORE,
    CASE_NORMAL,
)


Condition = namedtuple('Condition', [
    'text',
    'caret_locus',
    'selected_index',
    'matcher_index',
    'case_index',
])


class Lista(Prompt):
    """Lista class."""

    prefix = '# '

    sign_id_start = 90101
    signs_defined = []
    # timer_id = 0
    timer_active = False
    loop = asyncio.get_event_loop()
    active_timer = None
    callback_time = 250

    syntaxtype = 'buffer'  # 'lista', 'other'
    syntax = ''
    bufsyntax = ''

    key_matcher = 'C-^'  # until figure out how to fetch the keymap back properly
    key_case = 'C-_'
    key_syntax = 'C-s'

    statusline = ''.join([
        '%%#ListaStatuslineMode%s#%s%%#ListaStatuslineQuery#%s',
        '%%#ListaStatuslineFile# %s',
        '%%#ListaStatuslineIndicator# %d/%d',
        '%%#ListaStatuslineMiddle#%%=',
        # '%%#ListaStatuslineMode%s# %s ',
        '%%#ListaStatuslineMatcher%s# %s %%#ListaStatuslineKey#%s',
        '%%#ListaStatuslineCase%s# %s %%#ListaStatuslineKey#%s',
        '%%#ListaStatuslineSyntax%s# %s %%#ListaStatuslineKey#%s ',
    ])

    selected_index = 0

    matcher_index = 0

    case_index = 0

    @property
    def selected_line(self):
        if len(self._indices) and self.selected_index >= 0:
            return self._indices[self.selected_index] + 1
        return 0

    def __init__(self, nvim, condition):
        super().__init__(nvim)
        self._buffer = None
        self._indices = None
        self._previous = ''

        self._second = False

        self.action.register_from_rules(DEFAULT_ACTION_RULES)
        self.keymap.register_from_rules(nvim, DEFAULT_ACTION_KEYMAP)
        self.keymap.register_from_rules(
            nvim,
            nvim.vars.get('lista#custom_mappings', [])
        )
        # self.keymap...  # something to get switcher bindings for statusline
        self.highlight_group = nvim.vars.get('lista#highlight_group')
        if not self.highlight_group:
            self.highlight_group = 'Search'
        self.restore(condition)

    def start(self):
        bufhidden = self.nvim.current.buffer.options['bufhidden']
        self.nvim.current.buffer.options['bufhidden'] = 'hide'
        try:
            return super().start()
        finally:
            self.nvim.current.buffer.options['bufhidden'] = bufhidden

    def switch_matcher(self):
        self.matcher.current.remove_highlight()
        self.matcher.next()
        self._previous = ''

    def switch_case(self):
        self.case.next()
        self._previous = ''

    def switch_highlight(self):
        if self.syntaxtype != 'lista':
            self.syntaxtype, self.syntax = 'lista', 'lista'
        elif self.syntaxtype != 'buffer' and self.bufsyntax != 'lista':
            self.syntaxtype, self.syntax = 'buffer', self.bufsyntax
        else:
            return
        self.nvim.command('set syntax=' + self.syntax)
        self._previous = ''

    def get_ignorecase(self):
        if self.case.current is CASE_IGNORE:
            return True
        elif self.case.current is CASE_NORMAL:
            return False
        elif self.case.current is CASE_SMART:
            return not any(c.isupper() for c in self.text)

    def on_init(self):
        self._buffer = self.nvim.current.buffer
        # line below prob causing the manpage issues? since they have like weird socket names
        self._buffer_name = self.nvim.eval('simplify(expand("%:~:."))')
        self._content = list(map(
            lambda x: ANSI_ESCAPE.sub('', x),
            self._buffer[:]
        ))
        self._line_count = len(self._content)
        self._indices = list(range(self._line_count))
        self._bufhidden = self._buffer.options['bufhidden']
        self._buffer.options['bufhidden'] = 'hide'
        foldcolumn = self.nvim.current.window.options['foldcolumn']
        number = self.nvim.current.window.options['number']
        relativenumber = self.nvim.current.window.options['relativenumber']
        wrap = self.nvim.current.window.options['wrap']
        self.bufsyntax = self.nvim.current.buffer.options['syntax']
        if not self.bufsyntax:
            self.bufsyntax, self.syntax, self.syntaxtype = 'lista', 'lista', 'lista'

        self.nvim.command('noautocmd keepjumps enew')
        self.nvim.current.buffer[:] = self._content
        self.nvim.current.buffer.options['buftype'] = 'nofile'  # or nowrite?
        self.nvim.current.buffer.options['bufhidden'] = 'wipe'
        self.nvim.current.buffer.options['buflisted'] = False
        self.nvim.current.window.options['spell'] = False
        self.nvim.current.window.options['foldenable'] = False
        self.nvim.current.window.options['foldcolumn'] = foldcolumn
        self.nvim.current.window.options['colorcolumn'] = ''
        self.nvim.current.window.options['cursorline'] = True
        self.nvim.current.window.options['cursorcolumn'] = False
        self.nvim.current.window.options['wrap'] = wrap
        self.nvim.current.window.options['number'] = number
        self.nvim.current.window.options['relativenumber'] = relativenumber
        self.nvim.command('sign define ListaDummy')
        self.nvim.command('sign place 666 line=1 name=ListaDummy buffer=%d' % (
            self.nvim.current.buffer.number))

        if self.syntax != 'lista':
            self.syntax = self.bufsyntax
        self.nvim.command('set syntax=' + self.syntax)  # breaks on vimpager

        self.nvim.call('cursor', [self.selected_index + 1, 0])
        self.nvim.command('normal! zvzz')

        self._start_time = time.clock()

        return super().on_init()

    def on_redraw(self):
        prefix = self.prefix
        if self.insert_mode == INSERT_MODE_INSERT:
            insert_mode_name = 'insert'
        else:
            insert_mode_name = 'replace'
            prefix = 'R '

        if self.case.current == CASE_IGNORE:
            case_name = 'ignore'
        elif self.case.current == CASE_NORMAL:
            case_name = 'normal'
        elif self.case.current == CASE_SMART:
            case_name = 'smart'

        self.nvim.current.window.options['statusline'] = self.statusline % (
            insert_mode_name.capitalize(), prefix, self.text,
            self._buffer_name.split('/')[-1],
            len(self._indices), self._line_count,
            # insert_mode_name.capitalize(), insert_mode_name.upper()[:1],
            self.matcher.current.name.capitalize(),
            self.matcher.current.name, self.key_matcher,
            case_name.capitalize(),
            case_name, self.key_case,
            self.syntaxtype.capitalize(),
            self.syntax, self.key_syntax,
        )
        self.nvim.command('redrawstatus')
        return super().on_redraw()

    def on_update(self, status):
        previous = self._previous
        self._previous = self.text

        if not previous or not self.text.startswith(previous):
            self._indices = list(range(self._line_count))
            if previous and self.text:
                self.nvim.call(
                    'cursor',
                    [1, self.nvim.current.window.cursor[1]]
                )
        elif previous and previous != self.text:
            self.nvim.call('cursor', [1, self.nvim.current.window.cursor[1]])
        # elif keythatactuallydoesanything:

        # else:
        #     return

        ignorecase = self.get_ignorecase()
        self.matcher.current.filter(
            self.text,
            self._indices,
            self._content[:],
            ignorecase,
        )
        hit_count = len(self._indices)
        if hit_count < 1000:
            self.matcher.current.highlight(self.text,
                                           ignorecase,
                                           self.highlight_group)
        else:
            self.matcher.current.remove_highlight()

        assign_content(self.nvim, [self._content[i] for i in self._indices])

        # if self.timer_id:
            # self.nvim.command('call timer_stop(%d)' % self.timer_id)
        time_since_start = time.clock() - self._start_time
        if hit_count < 15:
            self.update_signs(hit_count)
        elif hit_count > 0 and hit_count < self._line_count and time_since_start > 0.035:
            limit = 5 * len(self.text)
            if limit > 30:
                limit = 30
            if hit_count > limit:
                hit_count = limit

            self.update_signs(hit_count) #throttle early
            # self.update_signs(20)
            # self.timer.cancel()
            # self.timer = Timer(1, self.nvim.async_call(self.callback_signs()))
            # self.timer.start()

            # self.loop = asyncio.get_event_loop()
            # loop.run_until_complete(self.timer_signs())
            # self.loop.call_later(0.25, self.timer_signs())

            # if self.active_timer:
            #     self.active_timer.cancel()
            # self.active_timer = self.loop.call_later(0.20, self.update_signs(20))


            # self.active_timer = self.loop.call_later(3.25, self.hurf())
            # self.active_timer.cancel()
            # # self.timer_signs()
            # # self.timer_id = self.nvim.command('call timer_start(%d, "<SID>callback_update"' % self.callback_time)
            # # self.timer_id = self.nvim.command("call timer_start(250, 'lista#start'")

        return super().on_update(status)

    def hurf(self):
        testy = self.nvim.current.buffer.number
        # self.nvim.command('verbose sign list')
        # self.nvim.command('sign define ListaLine1 text=1 texthl=GruvboxPurpleSign')

    def callback_signs(self):
        self.update_signs(len(self._indices))


    # NOTE: need to: put timer on other thread
    # then callback needs to do nvim.async_call, passing a python function on the main thread

    # async def timer_signs(self):
    #     # await asyncio.sleep(0.25)
    #     # update_signs(len(self.indices))
    #     while True:
    #         if self.timer_active:
    #             update_signs(len(self._indices))
    #             self.timer_active = False
    #             break
    #         else:
    #             self.timer_active = True
    #             await asyncio.sleep(0.25)

    def update_signs(self, hit_count = None):
        # if self._second:
        #     return
        # else:
        #     self._second = True

        if hit_count is None:
            hit_count = len(self._indices)
        elif hit_count == 0:
            return
        height = self.nvim.current.window.height
        if hit_count > height:
            hit_count = height
        buf_nr = self.nvim.current.buffer.number

        signs_placed = []

        for hit_line_index in range(0, hit_count):
            source_line_nr = self._indices[hit_line_index] + 1

            if source_line_nr not in self.signs_defined:
                highlight = 'Normal'
                if source_line_nr < 99:
                    highlight = 'GruvboxAquaSign'
                elif source_line_nr < 199:
                    highlight = 'GruvboxBlueSign'
                elif source_line_nr < 299:
                    highlight = 'GruvboxPurpleSign'
                elif source_line_nr < 399:
                    highlight = 'GruvboxGreenSign'
                elif source_line_nr < 499:
                    highlight = 'GruvboxYellowSign'
                elif source_line_nr < 599:
                    highlight = 'GruvboxOrangeSign'
                elif source_line_nr < 599:
                    highlight = 'GruvboxRedSign'
                index_text = str(source_line_nr)[-2:]  # 2: was causing the issue all along. how get right numbers?

                signdef = 'sign define ListaLine%d text=%s texthl=%s' % (
                    source_line_nr, index_text, highlight)
                self.nvim.command(signdef)
                self.signs_defined.append(source_line_nr)

            # all placed signs get reset to line 1 when content is
            # replaced. 
            signplace = 'sign place %d line=%d name=ListaLine%d buffer=%d' % (
                self.sign_id_start + hit_line_index, hit_line_index + 1,
                source_line_nr, buf_nr)

            # signs_placed.add(signplace)
            signs_placed.append(hit_line_index + 1)
            self.nvim.command(signplace)

        # self.nvim.command('silent! verbose sign place buffer')


    def on_term(self, status):
        self.matcher.current.remove_highlight()
        self.nvim.command('echo "%s" | redraw' % (
            '\n' * self.nvim.options['cmdheight']
        ))
        self.selected_index = self.nvim.current.window.cursor[0] - 1
        self.matcher_index = self.matcher.index
        self.case_index = self.case.index
        self.nvim.current.buffer.options['modified'] = False
        self.nvim.command('noautocmd keepjumps %dbuffer' % self._buffer.number)
        if self.text:
            ignorecase = self.get_ignorecase()
            caseprefix = '\c' if ignorecase else '\C'
            pattern = self.matcher.current.get_highlight_pattern(self.text)
            self.nvim.call('setreg', '/', caseprefix + pattern)
        return status

    def store(self):
        """Save current prompt condition into a Condition instance."""
        return Condition(
            text=self.text,
            caret_locus=self.caret.locus,
            selected_index=self.selected_index,
            matcher_index=self.matcher_index,
            case_index=self.case_index,
        )

    def restore(self, condition):
        """Load current prompt condition from a Condition instance."""
        self.text = condition.text
        self.caret.locus = condition.caret_locus
        self.selected_index = condition.selected_index
        self.matcher_index = condition.matcher_index
        self.case_index = condition.case_index
        self.matcher = Indexer(
            [AllMatcher(self.nvim), FuzzyMatcher(self.nvim)],
            index=self.matcher_index,
        )
        self.case = Indexer(CASES, index=self.case_index)
