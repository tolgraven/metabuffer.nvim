import time
# from threading import Timer
# import datetime
# import asyncio
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

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9a-zA-Z;]*?m')

CASE_SMART = 1
CASE_IGNORE = 2
CASE_NORMAL = 3
CASES = ( CASE_SMART, CASE_IGNORE, CASE_NORMAL,)

SYN_BUFFER = 0
SYN_BUILTIN = 1
SYNTAXES = ( SYN_BUFFER, SYN_BUILTIN,)
syntax_types = ['buffer', 'lista']  #will this ever be the extent of it with
# matchadd covering the rest, or can I come up with new categories? there is some
# way of combining properties of multiple syntax that I read about, look up.
# Ideal ofc if individual files of varying filetypes can each coexist properly
# highlighted within the metabuffer

Condition = namedtuple('Condition', [
    'text',
    'caret_locus',
    'selected_index',
    'matcher_index',
    'case_index',
    'syntax_index'
])


class Lista(Prompt):
    """Lista class."""

    prefix = '# '
    hotkey = {'matcher': 'C-^', 'case': 'C-_', 'syntax': 'C-s' }  # until figure out how to fetch the keymap back properly

    statusline = ''.join([
        '%%#ListaStatuslineMode%s#%s%%#ListaStatuslineQuery#%s',
        '%%#ListaStatuslineFile# %s',
        '%%#ListaStatuslineIndicator# %d/%d',
        '%%#Normal# %d',
        '%%#ListaStatuslineMiddle#%%=',
        # '%%#ListaStatuslineMode%s# %s ',
        '%%#ListaStatuslineMatcher%s# %s %%#ListaStatuslineKey#%s',
        '%%#ListaStatuslineCase%s# %s %%#ListaStatuslineKey#%s',
        '%%#ListaStatuslineSyntax%s# %s %%#ListaStatuslineKey#%s ',
    ]) # FIX!! show full line number for curr line in statusline.

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
        self._buffer, self._indices = None, None
        self._previous = ''

        self._previous_hit_count = 0
        self.sign_id_start = 90101
        self.signs_defined = []
        self.timer_active = False
        # self.loop = asyncio.get_event_loop()
        self.callback_time = 250

        self.action.register_from_rules(DEFAULT_ACTION_RULES)
        self.keymap.register_from_rules(nvim, DEFAULT_ACTION_KEYMAP)
        self.keymap.register_from_rules(nvim, nvim.vars.get('lista#custom_mappings', []))
        # self.keymap...  # something to get switcher bindings for statusline. Just parse out as str
        self.highlight_groups = nvim.vars.get('lista#highlight_groups', {})
        # self.syntax_state['active'] = nvim.vars.get('lista#syntax_init') or 'buffer'
        self.signs_enabled = nvim.vars.get('lista#line_nr_in_sign_column') or False
        self.restore(condition)

    def start(self):
        bufhidden = self.nvim.current.buffer.options['bufhidden']
        self.nvim.current.buffer.options['bufhidden'] = 'hide'
        try:
            return super().start()
        finally:
            self.nvim.current.buffer.options['bufhidden'] = bufhidden  #this is why scratch remains when shit throwns and that? must be

    def switch_matcher(self):
        self.matcher.current.remove_highlight()
        self.matcher.next()
        self._previous = ''

    def switch_case(self):
        self.case.next()
        self._previous = ''

    def switch_highlight(self):
        self.syntax.next()
        new_syntax = 'lista' if self.syntax.current is SYN_BUILTIN else self.buffer_syntax

        self.nvim.command('set syntax=' + new_syntax)
        self._previous = ''

    def get_ignorecase(self):
        if self.case.current is CASE_IGNORE:
            return True
        elif self.case.current is CASE_NORMAL:
            return False
        elif self.case.current is CASE_SMART:
            return not any(c.isupper() for c in self.text)

    def get_searchcommand(self):
        return self.searchcommand

    def on_init(self):
        self._buffer = self.nvim.current.buffer
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
        # something like this, but doesnt work this way. so maybe just loop?
        # foldcolumn, number, relativenumber, wrap = self.nvim.current.window.options['foldcolumn', 'number', 'relativenumber', 'wrap']

        #might nerdtree etc work if keep conceal active?
        conceallevel = self.nvim.current.window.options['conceallevel']

        self.nvim.command('noautocmd keepjumps enew')
        self.nvim.current.buffer[:] = self._content
        buf_opts = {'buftype': 'nofile', 'bufhidden': 'wipe', 'buflisted': False,}
        win_opts = {'spell': False, 'foldenable': False, 'foldcolumn': foldcolumn,
                    'colorcolumn': '', 'cursorline': True, 'cursorcolumn': False,
                    'wrap': wrap, 'relativenumber': relativenumber, 'number': number,
                    'conceallevel': conceallevel, 
                    }
        for opt,val in buf_opts.items():
            self.nvim.current.buffer.options[opt] = val
        for opt,val in win_opts.items():
            self.nvim.current.window.options[opt] = val
        self.nvim.command('sign define ListaDummy')
        if self.signs_enabled:  #should also place dummy if there were signs placed/signcolumn visible, so layout stays the same
          self.nvim.command('sign place 666 line=1 name=ListaDummy buffer=%d' % (
              self.nvim.current.buffer.number))

        if not self.buffer_syntax:  #something went wrong getting syntax from vim, use strictly lista's own
            self.buffer_syntax = syntax_types[SYN_BUILTIN]
            self.syntax.index = SYN_BUILTIN
        self.nvim.command('set syntax=' + self.buffer_syntax)  #init at index 0 = buffer, for now. Consistent with the others, but can't be hardset later when more appear
        # need to set syntax up here instead of on_redraw like the other stuff, dont want to set that every time, only on changes, right?
        self.nvim.call('cursor', [self.selected_index + 1, 0])
        self.nvim.command('normal! zvzz')

        self._start_time = time.clock()

        return super().on_init()

    def on_redraw(self):
        prefix = self.prefix
        if self.insert_mode is INSERT_MODE_INSERT:
            insert_mode_name, prefix = 'insert', '# '
        else:
            insert_mode_name, prefix = 'replace', 'R '
        case_name = 'ignore' if self.case.current is CASE_IGNORE else 'normal' if self.case.current is CASE_NORMAL else 'smart'
        
        if self.syntax.current is SYN_BUFFER:
          hl_prefix, syntax_name = 'Buffer', self.buffer_syntax
        elif self.syntax.current is SYN_BUILTIN:
          hl_prefix, syntax_name = 'Lista', 'lista'

        self.nvim.current.window.options['statusline'] = self.statusline % (
            insert_mode_name.capitalize(), prefix, self.text,
            self._buffer_name.split('/')[-1],               # filename without path
            len(self._indices), self._line_count,           # hits / lines
            (self.selected_index or 0) + 1,                 # line under cruisor
            self.matcher.current.name.capitalize(), self.matcher.current.name, self.hotkey['matcher'],
            case_name.capitalize(), case_name, self.hotkey['case'],
            hl_prefix, syntax_name, self.hotkey['syntax'],
        )
        self.nvim.command('redrawstatus')
        return super().on_redraw()

    def on_update(self, status):
        previous, self._previous = self._previous, self.text
        previous_hit_count = len(self._indices)

        if not previous or not self.text.startswith(previous):  # new, restarted or backtracking
            self._indices = list(range(self._line_count))       #reset index list
            if previous and self.text:                          #if we didnt delete the last char?
                self.nvim.call( 'cursor', [1, self.nvim.current.window.cursor[1]])
        elif previous and previous != self.text:                #if query has changed
            self.nvim.call('cursor', [1, self.nvim.current.window.cursor[1]])
        ignorecase = self.get_ignorecase()
        self.matcher.current.filter( self.text, self._indices, self._content[:], self.get_ignorecase())
        hit_count = len(self._indices)
        if hit_count < 1000:
          syn = syntax_types[SYN_BUFFER] if self.syntax.current is SYN_BUFFER \
                                       else syntax_types[SYN_BUILTIN]
          hl = self.highlight_groups[syn]
          self.matcher.current.highlight(self.text, ignorecase, hl)  #highlights instances with the appropriate highlighting group
        else:
            self.matcher.current.remove_highlight()
        if previous_hit_count != hit_count:  # should use more robust check since we can of course end up with same amount, but different hits
            assign_content(self.nvim, [self._content[i] for i in self._indices])
            if self.signs_enabled:
              self.nvim.command('sign unplace * buffer=%d' % self.nvim.current.buffer.number)  #no point not clearing since all end up at line 1...
              self.nvim.command('sign place 666 line=1 name=ListaDummy buffer=%d' % self.nvim.current.buffer.number)

        # if self.timer_id:
            # self.nvim.command('call timer_stop(%d)' % self.timer_id)
        time_since_start = time.clock() - self._start_time
        if hit_count < 15:
            self.update_signs(hit_count)

        elif hit_count < self._line_count and time_since_start > 0.035:
            sign_limit = min(5 * len(self.text), 25)
            self.update_signs(min(hit_count, sign_limit))
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
            # # self.timer_id = self.nvim.command('call timer_start(%d, "<SID>callback_update"' % self.callback_time)
            # 

        return super().on_update(status)

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

    def update_signs(self, hit_count = None, jump_to_next = 1):
        if not self.signs_enabled:
            return
        hit_count = hit_count or len(self._indices)
        win_height = self.nvim.current.window.height
        buf_nr = self.nvim.current.buffer.number

        colors = ['ListaSign' + color for color in
                  ['Aqua', 'Blue', 'Purple', 'Green', 'Yellow', 'Orange', 'Red']]

        signs_placed = []

        for hit_line_index in range(min(hit_count, win_height)):
            source_line_nr = self._indices[hit_line_index] + 1

            if source_line_nr not in self.signs_defined:
                highlight = next((colors[x] for x in range(len(colors))
                                  if x*100 + 99 >= source_line_nr),
                                  'Normal')
                index_text = str(source_line_nr)[-2:]

                sign_to_define = 'sign define ListaLine%d text=%s texthl=%s' % (
                    source_line_nr, index_text, highlight)
                self.nvim.command(sign_to_define)
                self.signs_defined.append(source_line_nr)

            # remember all placed signs get reset to line 1 when content is replaced. 
            sign_to_place = 'sign place %d line=%d name=ListaLine%d buffer=%d' % (
                self.sign_id_start + hit_line_index, hit_line_index + 1,
                source_line_nr, buf_nr)

            signs_placed.append(hit_line_index + 1)
            self.nvim.command(sign_to_place)


    def on_term(self, status):
        self.matcher.current.remove_highlight()   #not on pause tho I guess?
        self.nvim.command('echo "%s" | redraw' % (
            '\n' * self.nvim.options['cmdheight']
        ))
        self.selected_index = self.nvim.current.window.cursor[0] - 1
        self.matcher_index = self.matcher.index
        self.case_index = self.case.index
        self.syntax_index = self.syntax.index
        self.nvim.current.buffer.options['modified'] = False  #do we leave a
        # filtered dummy buffer as modified and hence revertible? not really
        # feasible or necessary since reverting ought to imply wiping the
        # scratch. But I think a buffer that has been paused, and then isn't
        # resumed but just has a new instance ran on top of it, should have that
        # filtered selection as a starting point, treated like any other buffer -
        # BUT that's where you tart requiring metadata for every single line...
        # hmm. Especially if you go back and forth between filtering and actual
        # editing...

        # this one def not when pausing...
        self.nvim.command('noautocmd keepjumps %dbuffer' % self._buffer.number)
        if self.text:
            caseprefix = '\c' if self.get_ignorecase() else '\C'
            pattern = self.matcher.current.get_highlight_pattern(self.text)
            self.searchcommand = caseprefix + pattern
            # self.nvim.call('setreg', '/', caseprefix + pattern)  #prep, but dont execute, HL search. Pop up on next n/N. Could set so auto-hl's only if pressed enter, not esc

            #when multiple search words we really should use matchadd() too tho # to separate multiple terms. Plus that add the possibility
            # of highlighting this way while filtering, and setting hue to match filter-outs and stuff.
            # Get on stealing that, fzf was it?, ez-mode regex engine

        return status

    def store(self):
        """Save current prompt condition into a Condition instance."""
        return Condition(
            text=self.text,
            caret_locus=self.caret.locus,
            selected_index=self.selected_index,
            matcher_index=self.matcher_index,
            case_index=self.case_index,
            syntax_index=self.syntax_index,
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
        self.syntax_index = condition.syntax_index
        self.syntax = Indexer(SYNTAXES, index=self.syntax_index)

