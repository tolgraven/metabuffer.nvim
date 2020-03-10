import time
import re
from collections import namedtuple
from meta.prompt.prompt import (  # type: ignore
    INSERT_MODE_INSERT, INSERT_MODE_REPLACE, Prompt, Condition)
from .action import DEFAULT_ACTION_KEYMAP, DEFAULT_ACTION_RULES
from .modeindexer import ModeIndexer
from .matcher.all import Matcher as AllMatcher
from .matcher.fuzzy import Matcher as FuzzyMatcher
from .matcher.regex import Matcher as RegexMatcher
from .buffer.metabuffer import Buffer as MetaBuffer
from .window.metawindow import Window as MetaWindow
# from .util import ???
import logging
logfile = '/Users/tol/meta.log'
level = logging.DEBUG

cases = ['smart', 'ignore', 'normal']
syntax_types = ['buffer', 'meta']  # will this ever be the extent of it with matchadd covering rest, or I suppose 'mixed' (region, like in markdown...) a given later. +there is some way of combining properties of multiple syntax that I read about, look up.  Ideal ofc if individual files of varying filetypes can each coexist properly highlighted within the metabuffer, which is also supposedly possible...

extra_cond = ('selected_index',     # selected line (out of curr visible)
              'matcher_index', 'case_index', 'syntax_index',
              'restored',)
Condition = namedtuple('Condition', Condition._fields + extra_cond)
def default_condition(nvim, query):
  """Should go in proper State class hey"""
  return Condition(text=query, caret_locus=len(query),
                    selected_index=nvim.current.window.cursor[0] - 1,
                    matcher_index=0, case_index=0, syntax_index=0,
                    restored=False)

class Meta(Prompt):
    """Meta class. Shouldn't inherit from Prompt in long run...
    Or rather, Keep as-is but with something else wrapping..."""

    _prefix = '# '
    mode = {}
    selected_index = 0            # selected line index out of current filter view
    updates = 0
    debug_out = ''
    # callback_time = 500
    # timer_id = 0
    _prev_text = ''                # Latest entered query, so can compare incoming

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
      """Get (actual) line number of selection.
      Mind buf.indices curr returns filtered variety.
      Jump on _ACCEPT working correctly, but not statusline prompt..."""
      return self.buf.source_line_nr(self.selected_index)

    @property
    def prefix(self):
      """Insert/replace mode prompt prefix. Expand for Normal etc..."""
      return 'R' if self.insert_mode is INSERT_MODE_REPLACE else self._prefix

    @property
    def vim_query(self): #
      """Vim search query to run after (not-yet-)Meta _ACCEPT finish.  should go
      outside class tho, or well can/will use straight vim stuff later on while
      running. hmm..."""
      if not self.text: return ''

      caseprefix = r'\c' if self.ignorecase else r'\C'
      pattern = self.matcher.get_highlight_pattern(self.text)
      return caseprefix + pattern

    @property
    def hit_count(self): return len(self.buf.indices)

    def switch_mode(self, mode_indexer):
      """Switch a stepping setting to its next value"""
      self.mode[mode_indexer].next()
      self._prev_text = ''                                     # Force rerun query from start


    def __init__(self, nvim, state):
        logging.basicConfig(filename=logfile, level=level)
        logging.warning('abc')    # apparently broken by pynvim? lol
        super().__init__(nvim)

        self.action.register_from_rules(DEFAULT_ACTION_RULES)
        for keys in [DEFAULT_ACTION_KEYMAP,
                     nvim.vars.get('meta#custom_mappings', [])]:  # something to get switcher bindings for statusline.  just ad to custom_keys eh..
          self.keymap.register_from_rules(nvim, keys)             # XXX all unrecognized input keys should pause and/or passthrough to vim i guess?

        self.highlight_groups = nvim.vars.get('meta#highlight_groups', {})
        self.signs_enabled = nvim.vars.get('meta#line_nr_in_sign_column') or False

        self.restore(state)

        self.mode['matcher'] = ModeIndexer([AllMatcher(self.nvim),    # TODO Prob ev pass MetaBuffer obj rather than nvim, so matchers use our abstractions
                                            FuzzyMatcher(self.nvim),
                                            RegexMatcher(self.nvim)],
                                           state.matcher_index or 0,
                                           on_leave = 'remove_highlight')
        self.mode['case'] = ModeIndexer(cases,
                                        state.case_index or 0)

        f = lambda syn: self.buf.apply_syntax('meta' if syn.current is 'meta' else None)
        self.mode['syntax'] = ModeIndexer(syntax_types,
                                          state.syntax_index or 0,
                                          on_active = f) #temp since Buffer will handle but yeah
                        # oh yeah never actually updates outside indexer, hence... but dont fuck w it until everything's moved out

        view = self.nvim.call('winsaveview')  # get a weirdo jump on term instead with this...
        self.win = MetaWindow(self.nvim)
        self.buf = MetaBuffer(self.nvim, self.nvim.current.buffer)  # also inits content etc...
        self.model_buf = self.buf.model
        self.nvim.call('winrestview', view)  # test


    def start(self):
        self.buf.push_opt('bufhidden', 'hide')
        try:
          return super().start()
        finally:
          self.buf.pop_opt('bufhidden')
          self.matcher.remove_highlight() #should be in matcher dtor i guess


    def on_init(self):
        self.buf.apply_syntax() # XXX restore checking for failure getting buffer syntax...
        self.nvim.call('cursor', [self.selected_index + 1, 0])
        # self.nvim.command('normal! zvzz')  #thought this killed folds but that obvs happens automatically since we're in a new buffer, seems
        # zv 'view cursor line: open just enough folds to make the line in which the cursor is located not folded'
        # zz 'redraw, make cursor line centered in window' seems dumb, we want to avoid jumps in view when entering meta mode, as much as possible...
        self._start_time = time.clock()
        return super().on_init()


    def on_redraw(self):
        """Prompt redraw of window statusline. In future hook (like rest) to """
        mode_name = 'replace' if self.insert_mode is INSERT_MODE_REPLACE else 'insert'
        hl_prefix = 'Faded'   if self.buf.syntax is 'meta' else 'Buffer'
        self.win.set_statusline(mode_name, self.prefix, self.text,
                                self.buf.name_short,   # filename without path
                                len(self.buf.indices), # hits
                                self.buf.line_count,   # lines
                                # (self.selected_index or 0) + 1,  # line under cruisor
                                self.selected_line or 0,  # line under cruisor
                                self.debug_out,        # DEBUG DUMP:
                                self.matcher.name, self.case,
                                hl_prefix, self.buf.syntax)

        self.nvim.command('redrawstatus')
        return super().on_redraw()

    def update_prev(self):
        """Assuming there'll be more things to stash on update?"""
        prev = self._prev_text
        self._prev_text = self.text
        return [prev, self.buf.indices[:], len(self.buf.indices)]


    def on_update(self, status): # prompt update
        prev_text, prev_hits, prev_hit_count = self.update_prev()
        self.updates += 1
        logging.info('WTF IS WRONG')    # apparently broken by pynvim? lol

        # this one just lies in these instances...  [2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 42, 115, 122, 125, 256, 310]
        # prev_selected = self.nvim.current.window.cursor[0] - 1      # in ex: is 10.
        prev_selected = self.selected_index                         # selected_index not cursor yada, so incl get from restore
        prev_line_nr = self.buf.source_line_nr(prev_selected)       # in ex, 14 except we're getting 11 when actually run. why m.buf.indices[10] + 1 = 14

        reset_if = not prev_text or not self.text.startswith(prev_text)
        self.buf.run_filter(self.matcher, self.text, self.ignorecase, reset_if)
        #  # still yucky but better encapsulated like this yeah?  same goes for rest tho - all buf internal shit

        curr_line_nr = self.buf.source_line_nr(prev_selected)       # makes sense turns None
        our_idx = None
        # if prev_hit_count != self.hit_count and prev_hits != self.buf.indices:  # so first compare count THEN double-check indexes changed
        if prev_hits != self.buf.indices:  # makes sense - do any indexes differ? then run...
          self.buf.update()   # display filter from above. remember winstore+winrestview called inside here

          if curr_line_nr != None and prev_line_nr != curr_line_nr:  # if same index means other src line, react...
            try:
              our_idx = self.buf.indices.index(prev_line_nr - 1) # where is prev line nr hit now?
              # our_idx = self.buf.indices.index(prev_line_nr) - 1 # where is prev line nr hit now?
            except ValueError:    # our selected line has disappeared!
              our_idx = self.buf.closest_index(prev_line_nr - 1, False)   # after update we can ensure on right line
            finally:
              if our_idx != None and our_idx != 0: #temp test ooook ugly hack sorta works for now.
                self.win.set_row(our_idx + 1)  # line is _gone_ and if it's simply shifted
                # self.selected_index = self.nvim.current.window.cursor[0] - 1
            # ok still dont get why jumps upwards and returns lowballin when shouldnt
            # uglyhack semi-work for now - skip our_idx if 0.  so only works when due to our_idx ret 0, not when just low
            # only resume investigation WHEN FUCKING GOT THE TOOLS FOR IT UGH
            # also def stuff still off line_nr vs index +- 1 bs


        self.debug_out = ' idx p/n %d/%d line p/n %d/%d newidx %d, up(%d)' % \
          (prev_selected, self.nvim.current.window.cursor[0] - 1,
           prev_line_nr if prev_line_nr != None else -1,
           curr_line_nr if curr_line_nr != None else -1,
           our_idx if our_idx != None else -9,
           self.updates)

        self.selected_index = self.nvim.current.window.cursor[0] - 1

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
        extra = (self.selected_index,
                 *[self.mode[m].index for m in ['matcher', 'case', 'syntax']],
                 True,)
        return Condition(*(super().store() + extra)) # super useless and dumb (losing namedness right), just wanted to try >:)

    def restore(self, condition):
        """Load current prompt condition from a Condition instance."""
        super().restore(condition)
        self.selected_index = condition.selected_index
        self.restored = condition.restored  # seems somehow superflous but eh

