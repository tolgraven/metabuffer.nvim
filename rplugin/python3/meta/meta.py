"""Main Meta runner/Prompt class"""
import time
from collections import namedtuple
from meta.prompt.prompt import (  # type: ignore
    INSERT_MODE_INSERT, INSERT_MODE_REPLACE, Prompt, Condition,
    STATUS_ACCEPT, STATUS_CANCEL, STATUS_INTERRUPT, STATUS_PROGRESS, STATUS_PAUSE)
from meta.action import DEFAULT_ACTION_KEYMAP, DEFAULT_ACTION_RULES
from meta.modeindexer import ModeIndexer
from meta.matcher.all   import Matcher as AllMatcher
from meta.matcher.fuzzy import Matcher as FuzzyMatcher
from meta.matcher.regex import Matcher as RegexMatcher
from meta.buffer.metabuffer import Buffer as MetaBuffer
from meta.window.metawindow import Window as MetaWindow
from meta.window.floating   import Window as FloatingWindow
# from .util import ???
import logging

cases = ['smart', 'ignore', 'normal']
syntax_types = ['buffer', 'meta']  # will this ever be the extent of it with matchadd covering rest, or I suppose 'mixed' (region, like in markdown...) a given later. +there is some way of combining properties of multiple syntax that I read about, look up.  Ideal ofc if individual files of varying filetypes can each coexist properly highlighted within the metabuffer, which is also supposedly possible...

extra_cond = ('selected_index',     # selected line (out of curr visible)
              'matcher_index', 'case_index', 'syntax_index',
              'restored',)
Condition = namedtuple('Condition', Condition._fields + extra_cond)
def default_condition(nvim, query = ''):
  """Should go in proper State class hey"""
  return Condition(text=query, caret_locus=len(query),
                    selected_index=nvim.current.window.cursor[0] - 1,
                    matcher_index=0, case_index=0, syntax_index=0,
                    restored=False)
# something like this def makes most sense in long run hah. Also: ffs dont try
# wrangle python too much until refreshed my knowledge lol
# class PromptState(Condition):
  # def __init__(self, condition = Condition(text = '', caret_locus = 0),
  #              selected_index = 0, matcher_index = 0, case_index = 0,
  #              syntax_index = 0, restored = False):


class Meta(Prompt):
    """Meta class. Shouldn't inherit from Prompt in long run...
    Or rather, Keep as-is but with something else wrapping...
    Turns out Coc multiple-cursor plug (of all things lol) actually does
    p much exactly core workflow in "refactor mode" or something, just with
    slightly more limited (aka... defined) scope.
    So def take a look there. Both LSP integration and abstracting away push
    (just write dummy buffer to push)"""

    _prefix = '# '
    mode = {}
    # callback_time = 500

    @property
    def matcher(self): return self.mode['matcher'].current
    @property
    def case(self):    return self.mode['case'].current
    @property
    def syntax(self):  return self.mode['syntax'].current

    @property
    def ignorecase(self): # so these should really be a dict name/eval
        if self.case == 'ignore':   return True
        elif self.case == 'normal': return False
        elif self.case == 'smart':
            return not any(c.isupper() for c in self.text)

    @property
    def selected_line(self):
      """Get (actual) line number of selection.
      Mind buf.indices curr returns filtered variety.
      Jump on _ACCEPT working correctly, but not statusline prompt..."""
      return self.buf.source_line_nr(self.selected_index)

    @property
    def line_nr(self):
      return self.nvim.current.window.cursor[0]
      # return self.selected_index+1
    @line_nr.setter
    def line_nr(self, val):
      self.win.set_row(val)
      self.selected_index = max(val-1, 0)

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

    @property
    def query(self) -> str: return self.text
    @query.setter
    def query(self, new_text):
      """This bound to fuck up Prompt updates tho or?"""
      self._prev_text = self.text
      self.text = new_text

    def switch_mode(self, mode_indexer):
      """Switch a stepping setting to its next value"""
      self.mode[mode_indexer].next()
      self._prev_text = ''                                     # Force rerun query from start


    def __init__(self, nvim, state):
        """Less wasting time, some things to test:
        1. Make a Buffer with all loaded bufs as content
        2. Fix the callback stuff to add transform steps to buffers
        3. Ditto, views - how makes most sense
        4. Maybe Window easiest to start assembling the compound structure
            (orig, floating showstuff, next prompt additional)
        5. Bc good and future way of doing things etc
            but in short-term also v nice debugging,
            try Prompt instance w mainloop of only Autocmd...
            No keys or anything just survey textbuf

            """
        super().__init__(nvim)

        self.selected_index, self._prev_text = 0, ''            # selected line index out of current filter view
        self.updates, self.debug_out = 0, ''
        self.fwin = None
        # timer_id = 0
        # self._prev_text = ''                # Latest entered query, so can compare incoming

        self.action.register_from_rules(DEFAULT_ACTION_RULES)
        for keys in [DEFAULT_ACTION_KEYMAP,
                     nvim.vars.get('meta#custom_mappings', [])]:  # something to get switcher bindings for statusline.  just ad to custom_keys eh..
          self.keymap.register_from_rules(nvim, keys)             # XXX all unrecognized input keys should pause and/or passthrough to vim i guess?

        self.highlight_groups = nvim.vars.get('meta#highlight_groups', {})
        # actual MetaFaded: parse "all" users hi groups, temp override by
        # desat/dimmed version. Better focus on char-hl without losing syntax
        # Not so tricky, already got the group -> colorfg
        # easy so...
        self.signs_enabled = nvim.vars.get('meta#line_nr_in_sign_column') or False

        self.restore(state)

        self.mode['matcher'] = ModeIndexer([AllMatcher(self.nvim),    # TODO Prob ev pass MetaBuffer obj rather than nvim, so matchers use our abstractions
                                            FuzzyMatcher(self.nvim),
                                            RegexMatcher(self.nvim)],
                                           state.matcher_index or 0,
                                           on_leave = 'remove_highlight')
        self.mode['case'] = ModeIndexer(cases,
                                        state.case_index or 0)

        f = lambda syn: self.buf.apply_syntax('meta' if syn.current == 'meta' else None)
        self.mode['syntax'] = ModeIndexer(syntax_types,
                                          state.syntax_index or 0,
                                          on_active = f) #temp since Buffer will handle but yeah

        # view = self.nvim.call('winsaveview')  # get a weirdo jump on term instead with this...
        self.win = MetaWindow(self.nvim)
        self.buf = MetaBuffer(self.nvim, self.nvim.current.buffer)  # also inits content etc...
        # self.buf.add_view()
        # self.nvim.call('winrestview', view)  # test


    def start(self):
        # self.buf.push_opt('bufhidden', 'hide')
        self.fwin = self.fwin or FloatingWindow(self.nvim, self.buf.indexbuf.buffer) #gets created but switches both bufs
        MetaBuffer.switch_buf(self.nvim, self.buf.buffer) #ensure looking at right thing when restarting...
        try:
          return super().start()    # enters main loop so wont return until finished...
        except Exception as e:
          self.nvim.err_write('%s' % e.__traceback__)
        finally:
          # self.buf.pop_opt('bufhidden')
          self.matcher.remove_highlight() #should be in matcher dtor i guess
          self.nvim.current.buffer.options['modified'] = False  # obvs filtered buffer is not "modified" since only actual subsecquent edits are supposed to count as that, and filtering is something else, decoupled


    def on_init(self):
        self.buf.apply_syntax() # XXX restore checking for failure getting buffer syntax...
        self.nvim.call('cursor', [self.selected_index + 1, 0])
        # self.runcmdz = [self.win.set_cursor, self.selected_index + 1]    # needed so dont start on line1
        # but when restoring I suppose this makes first  jump before filltering is done ->
        # wrong index base right?

        # self.nvim.command('normal! zvzz')  #thought this killed folds but that obvs happens automatically since we're in a new buffer, seems
        # zv 'view cursor line: open just enough folds to make the line in which the cursor is located not folded'
        # zz 'redraw, make cursor line centered in window' seems dumb, we want to avoid jumps in view when entering meta mode, as much as possible...
        # self._start_time = time.clock()
        return super().on_init()


    def on_redraw(self):
        """Prompt redraw of window statusline. In future hook (like rest) to """
        mode_name = 'replace' if self.insert_mode is INSERT_MODE_REPLACE else 'insert'
        hl_prefix = 'Faded'   if self.buf.syntax == 'meta' else 'Buffer'
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

    def update_prev(self, new_text=''):
        """Assuming there'll be more things to stash on update?"""
        # if new_text: self.text = new_text
        prev = self._prev_text
        self._prev_text = self.text   # seems more sensible to handle on actual update or guess not if multiple changes, which will happen down line
        # in which case, skip this sillyness and just update _prev at end of handling?
        # then can continue to compare self.prev to .text no prob
        return [prev, self.buf.indices[:], len(self.buf.indices)]


    def on_update(self, status): # prompt update
        prev_text, prev_hits, prev_hit_count = self.update_prev()
        self.updates += 1

        # this one just lies in these instances...  [2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 42, 115, 122, 125, 256, 310]
        # prev_selected = self.nvim.current.window.cursor[0] - 1      # in ex: is 10.
        prev_selected = self.selected_index                         # selected_index not cursor yada, so incl get from restore
        prev_line_nr = self.buf.source_line_nr(prev_selected)       # in ex, 14 except we're getting 11 when actually run. why m.buf.indices[10] + 1 = 14

        reset_if = not prev_text or not self.text.startswith(prev_text)
        self.buf.run_filter(self.matcher, self.text, self.ignorecase, reset_if)
        #  # still yucky but better encapsulated like this yeah?  same goes for rest tho - all buf internal shit

        # curr_line_nr = self.buf.source_line_nr(prev_selected)       # makes sense turns None
        # if lines jump on content replace like mentioned in gh issues then
        # we'll need to either restore pos, or get updated selection right?
        # self.line_nr = prev_selected + 1 # try restore prior pos?
        # curr_line_nr = self.buf.source_line_nr(self.nvim.current.window.cursor[0] - 1)       # makes sense turns None
        curr_line_nr = None
        our_idx = None
        # if prev_hit_count != self.hit_count and prev_hits != self.buf.indices:  # so first compare count THEN double-check indexes changed
        if prev_hits != self.buf.indices:  # makes sense - do any indexes differ? then run...
          self.buf.update()   # display filter from above. remember winstore+winrestview called inside here
          curr_line_nr = self.buf.source_line_nr(self.nvim.current.window.cursor[0] - 1)       # makes sense turns None
          # self.nvim.current.window.cursor
          # self.nvim.call('cursor', [self.selected_index + 1, 0])

          if curr_line_nr != None and prev_line_nr != curr_line_nr:  # if same index means other src line, react...
            try:
              our_idx = self.buf.indices.index(prev_line_nr - 1) # where is prev line nr hit now?
            except ValueError:    # our selected line has disappeared!
              our_idx = self.buf.closest_index(prev_line_nr - 1, False)   # after update we can ensure on right line
            finally:
              if our_idx != None and our_idx != 0: #temp test ooook ugly hack sorta works for now.
                self.line_nr = our_idx+1
                # self.win.set_row(our_idx + 1)  # line is _gone_ and if it's simply shifted
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

        # self.selected_index = self.nvim.current.window.cursor[0] - 1

        # self.handle_signs(hit_count)
        return super().on_update(status)


    def callback_signs(self):
        self.update_signs(len(self._indices))

    def handle_signs(self, hit_count):
        # if self.signs_enabled: signs.thing_in_on_update()

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
        if status is STATUS_ACCEPT:
          if self.fwin:
            self.nvim.api.win_close(self.fwin.window.handle, False)
        elif status is STATUS_PAUSE:
          pass
          # keep view of alt buf, dont nuke window...
        # self.nvim.command('echomsg "%s" | redraw' % ( '\n' * self.nvim.options['cmdheight']))  #put spacer I guess, fuckit
        # self.selected_index = self.nvim.current.window.cursor[0] - 1 # XXX only needs doing if not updating continously - which shouldn't be the case
        self.nvim.current.buffer.options['modified'] = False  # obvs filtered buffer is not "modified" since only actual subsecquent edits are supposed to count as that, and filtering is something else, decoupled

        # if self.text:  # contents of propt when finishing...
        #     self.matcher.remove_highlight() #for now. different when we own window..
        return status

    def store(self):
        """Save current prompt condition into a Condition instance."""
        extra = (self.selected_index,
                 *[self.mode[m].index for m in ['matcher', 'case', 'syntax']],
                 True,)
        return Condition(*(super().store() + extra)) # super useless and dumb (losing namedness right), just wanted to try >:)

    def restore(self, condition: Condition):
        """Load current prompt condition from a Condition instance."""
        super().restore(condition)
        self.selected_index = condition.selected_index
        self.restored = condition.restored  # seems somehow superflous but eh

