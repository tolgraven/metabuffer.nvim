import time
import re
from collections import namedtuple
from meta.prompt.prompt import (  # type: ignore
    INSERT_MODE_INSERT, INSERT_MODE_REPLACE, Prompt,
)
from .action import DEFAULT_ACTION_KEYMAP, DEFAULT_ACTION_RULES
from .modeindexer import ModeIndexer
from .matcher.all import Matcher as AllMatcher
from .matcher.fuzzy import Matcher as FuzzyMatcher
from .matcher.regex import Matcher as RegexMatcher
from .buffer.regular import Buffer as RegularBuffer
from .buffer.metabuffer import Buffer as MetaBuffer
from .window.metawindow import Window as MetaWindow
from .util import assign_content

# ANSI_ESCAPE = re.compile(r'\x1b\[[0-9a-zA-Z;]*?m')

cases = ['smart', 'ignore', 'normal']
syntax_types = ['buffer', 'meta']  # will this ever be the extent of it with # matchadd covering the rest, or can I come up with new categories? there is some way of combining properties of multiple syntax that I read about, look up.
# Ideal ofc if individual files of varying filetypes can each coexist properly highlighted within the metabuffer, which is also supposedly possible...
Condition = namedtuple('Condition', [
    'text', 'caret_locus',
    'selected_index', 'matcher_index', 'case_index', 'syntax_index',
    'restored', ])


class Meta(Prompt):
    """Meta class."""

    _prefix = '# '
    mode = {}
    selected_index = 0 # index = {'selected': 0. yada...}
    callback_time = 500
    timer_id = 0

    @property
    def matcher(self): return self.mode['matcher'].current
    @property
    def case(self):    return self.mode['case'].current
    @property
    def syntax(self):  return self.mode['syntax'].current

    @property
    def ignorecase(self): # so these should really be a dict name/eval
        if self.case is 'ignore':   return True
        elif self.case is 'normal': return False
        elif self.case is 'smart':
            return not any(c.isupper() for c in self.text)

    @property
    def selected_line(self):
        if len(self.buf.indices) and self.selected_index >= 0:
            return self.buf.indices[self.selected_index] + 1
        return 0

    @property
    def prefix(self):
      """Insert/replace mode prompt prefix. Expand for Normal etc..."""
      return 'R' if self.insert_mode is INSERT_MODE_REPLACE else self._prefix

    @property
    def origbuffer(self): return self.buf.model

    @property
    def vim_query(self): #should go outside class tho, or well can/will use straight vim stuff later on while running. hmm...
      """Vim search query to run after (not-yet-)Meta finish"""
      if not self.text: return ''

      caseprefix = r'\c' if self.ignorecase else r'\C'
      pattern = self.matcher.get_highlight_pattern(self.text)
      return caseprefix + pattern


    def __init__(self, nvim, saved_state): # add more args. f.ex. some action to take on exit...
        super().__init__(nvim)
        self._previous = ''
        self._previous_hit_count = 0

        self.action.register_from_rules(DEFAULT_ACTION_RULES)
        self.keymap.register_from_rules(nvim, DEFAULT_ACTION_KEYMAP)
        custom_keys = nvim.vars.get('meta#custom_mappings', [])
        self.keymap.register_from_rules(nvim, custom_keys) # self.keymap...  # something to get switcher bindings for statusline.  just ad to custom_keys eh..
        # XXX all unrecognized input keys should pause and/or passthrough to vim i guess?

        self.highlight_groups = nvim.vars.get('meta#highlight_groups', {})
        self.signs_enabled = nvim.vars.get('meta#line_nr_in_sign_column') or False

        self.restore(saved_state)

        self.mode['matcher'] = \
          ModeIndexer(
            [AllMatcher(self.nvim), FuzzyMatcher(self.nvim), RegexMatcher(self.nvim)],
            index=saved_state.matcher_index or 0,
            on_leave = 'remove_highlight')
        self.mode['case'] = \
            ModeIndexer(cases, saved_state.case_index or 0)

        f = lambda this: self.buf.apply_syntax('meta' if this.current is 'meta' else None)
        # switcher = lambda this: (
        #                     syn = 'meta' if this.current is 'meta' else None
        #                     self.buf.apply_syntax(syn))
        self.mode['syntax'] = ModeIndexer(syntax_types,
                                          saved_state.syntax_index or 0,
                                          on_active=f) #temp since Buffer will handle but yeah
                        # oh yeah never actually updates outside indexer, hence... but dont fuck w it until everything's moved out

        self.buf = MetaBuffer(self.nvim, self.nvim.current.buffer)
        self.win = MetaWindow(self.nvim)


    def start(self):
        self.buf.push_opt('bufhidden', 'hide')
        try:
          return super().start()
        finally:
          self.buf.pop_opt('bufhidden')
          self.matcher.remove_highlight() #should be in dtor i guess


    def switch_mode(self, mode_indexer):
      """Switch a stepping setting to its next value"""
      self.mode[mode_indexer].next()
      self._previous = '' #force rerun query from start
    def switch_matcher(self):   self.switch_mode('matcher') # til figure out sending args from vim. also obvs need setting directly
    def switch_case(self):      self.switch_mode('case')       # not stepping, whenexpanding to more stuff
    def switch_highlight(self): self.switch_mode('syntax')


    def on_init(self):
        self.buf.apply_syntax() # XXX restore checking for failure getting buffer syntax...
        self.nvim.call('cursor', [self.selected_index + 1, 0])
        # self.nvim.command('normal! zvzz')  #thought this killed folds but that obvs happens automatically since we're in a new buffer, seems
        # zv 'view cursor line: open just enough folds to make the line in which the cursor is located not folded'
        # zz 'redraw, make cursor line centered in window' seems dumb, we want to avoid jumps in view when entering meta mode, as much as possible...
        self._start_time = time.clock()
        return super().on_init()


    def on_redraw(self):
        mode_name = 'replace' if self.insert_mode is INSERT_MODE_REPLACE else 'insert'
        hl_prefix = 'Faded'   if self.buf.syntax is 'meta' else 'Buffer'
        self.win.set_statusline(mode_name, self.prefix, self.text,
                                self.buf.name_short,   # filename without path
                                len(self.buf.indices), # hits
                                self.buf.line_count,   # lines
                                (self.selected_index or 0) + 1,  # line under cruisor
                                self.matcher.name, self.case,
                                hl_prefix, self.buf.syntax)

        self.nvim.command('redrawstatus')
        return super().on_redraw()


    def on_update(self, status): # prompt update
        previous = self._previous
        self._previous = self.text

        win = self.nvim.current.window

        previous_hit_count = len(self.buf.filtered_indexes)
        if not previous or not self.text.startswith(previous):  # new, restarted or backtracking
            self.buf.reset_filter()
            # if previous and self.text:                          # there both was and is text. seems redundant lol
            #     self.nvim.call('cursor', [1, win.cursor[1]])
        # elif previous and previous != self.text:                # if query has changed
            # self.nvim.call('cursor', [1, win.cursor[1]])
        self.nvim.call('cursor', [1, win.cursor[1]])

        self.matcher.filter(self.text, self.buf.filtered_indexes,
                            self.buf.content[:], self.ignorecase) # ^  weird thing with regex matcher (which unlike others can end up with more chars AND more hits) if go eg 'function|return' only adds the return lines once hit backspace...
        # ^ the horror!! fix this uncouth unpure monstrosity.
        hit_count = len(self.buf.filtered_indexes)
        if hit_count < 1000:
          hl = 'MetaSearchHit' + self.matcher.name.capitalize()   # need multiple matches. inbetween fuzzy = faded bg of fuzzy fg.  regex wildcards/dots etc, ditto. check denite/fzf sources for how to...
          self.matcher.highlight(self.text, self.ignorecase, hl)  # highlights instances with the appropriate highlighting group
        else:
          self.matcher.remove_highlight()     #too much, man

        if previous_hit_count != hit_count:  # should use more robust check since we can of course end up with same amount, but different hits
          self.buf.update()

        # self.selected_index = self.nvim.current.window.cursor[0] - 1
        # still not updating even with it, but needs to be set somewhere right? dunno where i lost it

        # self.handle_signs(hit_count)
        return super().on_update(status)


    def callback_signs(self):
        self.update_signs(len(self._indices))

    def handle_signs(self, hit_count):
        if self.signs_enabled: signs.thing_in_on_update()

        time_since_start = time.clock() - self._start_time
        try:  self.nvim.call('timer_stop', self.timer_id)
        except: pass
        if hit_count < 15:
            self.signs.update(hit_count)
        elif hit_count < self._line_count and time_since_start > 0.035:
            sign_limit = min(5 * len(self.text), 25)
            self.signs.update(min(hit_count, sign_limit))
            self.timer_id = self.nvim.call('timer_start', self.callback_time, 'meta#callback_update')

    def update_signs(self, hit_count=None, jump_to_next=1):
        pass
        # self.signs.update(yada...)


    def on_term(self, status):
        # self.nvim.command('echomsg "%s" | redraw' % ( '\n' * self.nvim.options['cmdheight']))  #put spacer I guess, fuckit
        self.selected_index = self.nvim.current.window.cursor[0] - 1
        self.nvim.current.buffer.options['modified'] = False  # obvs filtered buffer is not "modified" since only actual subsecquent edits are supposed to count as that, and filtering is something else, decoupled
        if self.text:  # contents of propt when finishing...
            self.matcher.remove_highlight() #for now. different when we own window..

        return status

    def store(self):
        """Save current prompt condition into a Condition instance."""
        return Condition(
            text=self.text,
            caret_locus=self.caret.locus,
            selected_index=self.selected_index,
            matcher_index=self.mode['matcher'].index,
            case_index=self.mode['case'].index,
            syntax_index=self.mode['syntax'].index,
            restored=True,
        )

    def restore(self, condition):
        """Load current prompt condition from a Condition instance."""
        self.text = condition.text
        self.caret.locus = condition.caret_locus
        self.selected_index = condition.selected_index
        self.restored = condition.restored

