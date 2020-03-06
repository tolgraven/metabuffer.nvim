# from meta.handle import MetaHandle
from .base import AbstractBuffer
from copy import copy


class Buffer(AbstractBuffer):
  """A vim buffer not meant for end consumption, but as a malleable and
  temporary mirror"""
  name = 'metabuffer'

  default_opts = {'buftype': 'nofile',
                  'bufhidden': 'wipe',
                  'buflisted': False,}


  def __init__(self, nvim, model_buffer = None, opts = {}): # sending a (nvim, not meta) buffer to model. cause seems silly just taking over stuff that's how you break shit

    self.model = model_buffer or nvim.current.buffer #or can we set inn arg
    nvim.command('noautocmd keepjumps buffer %d' % self.model.number) #ensure src/model is active
    self.name = nvim.eval('simplify(expand("%:~:."))') #need override super which fetches from target.name?

    self._content = list(map(lambda x: self.ANSI_ESCAPE.sub('', x), self.model[:] ))
    self._indices = list(range(self.line_count)) #not to change
    self.filtered_indexes = copy(self._indices)

    nvim.command('noautocmd keepjumps enew') #create new

    super().__init__(nvim, nvim.current.buffer, opts)

    self.signs = self.nvim.command_output('silent sign place buffer=%d' % self.vim_id)
    self.has_signs = True if len(self.signs) > 2 else False

    self.update()


  def on_init(self):
    pass
    # self.sources = [self]         # a list of Buffer objects, together representing the total text content of this dummy buffer
    # self.rank = ranker # steal something from denite since we need to be able to sort, not the text within each source but the sources themselves
    # self.presentation = False        #like for dummy buffers, stuff to change presentation (whitespace, columns etc...) and other minor stuff, without touching original for those operations
    # self.content[:] = self.sources.join('\n')  #cause I guess we don't need/want dedicated setterart from constructor, just add sources and refresh rather?


    #for a dummy buffer it will mean the currently active syntax in vim,
    #for a backing buffer it will be its original syntax

  @property
  def content(self):    return self._content
  @property
  def line_count(self): return len(self.content)
  @property
  def indices(self):    return self.filtered_indexes #list(range(self.line_count))
  # def indices(self):    return self._indices #list(range(self.line_count))
  # @setter.filtered_indices
  # def filtered_indices(self):
  @property
  def all_indices(self):    return self._indices

  def reset_filter(self):
    self.filtered_indexes = copy(self._indices)

  @property
  def syntax(self):
    if self.syntax_type is 'buffer' and self.model.options['syntax']:
      return self.model.options['syntax']
    else:
      return 'meta'

  @property
  def name_short(self): return self.name.split('/')[-1]


  def update(self): # update shown content off any filter. but need further sep, have two Buffers for available vs. displayed content, then keep taking that concept further
    viewinfo = self.nvim.call('winsaveview')
    self.push_opt('modifiable', True)
    self.buffer[:] = [self.content[i] for i in self.filtered_indexes]
    self.pop_opt('modifiable')
    self.nvim.call('winrestview', viewinfo)


  def apply_syntax(self, syntax_type = None):
    """try get orig buffer syntax else fallback etc"""
    # self.syntax_orig = self.buffer.options['syntax']   #all buffers will have a syntax, even if it's "none"
    # if not self.syntax_orig:  # something went wrong getting syntax from vim, use strictly meta's own
    #     self.syntax = 'meta'
    if syntax_type: self.syntax_type = syntax_type
    self.nvim.command('set syntax=' + self.syntax)  # init at index 0 = buffer, for now. Consistent with the others, but can't be hardset later when more appear


  def idea(self, hmm):
    """what if we just make everything fully abstract and so everything is just
    a stack of operations. Or I mean we should keep better structure over stuff
    but ALSO keep something like that so that every single contribution (extra
    text, text filtered out, text edited...) can be taken out/changed or
    whatever, after the fact. Obvs would break or run against what we actually
    want, a lot, but can prob squeeze something p cool out of what does work.

    Oh and fucking hell are we involving text objects wrt filtering!! So here,
    write "def", and that'll mean all the lines in the current file with
    function definitions on them. Stack on some more individual files, or cmd
    like "all py files in folder", and a textobj filter, then cycle from like
    just lines with func defs, to all function bodies, etc"""

  def on_init(self):
    pass

  def on_term(self):
    pass

  def add(self, buffer):
    """Add/connect a Buffer source to the dummy buffer"""

  def text(self, text, matcher):
    """Get the full text representing the sources"""

  def filter(self, matcher):   # look closer at lista's filters and how fzr/denite etc do it.
    """Apply a semi-permanent filter limiting the contents in turn presented to
    matchers and available for modification"""

  def freeze(self, matcher):
    """Match text, but instead of hiding it, make it immutable/not propogate
    back to its originating buffer (+ i guess, when fucked with, restore it
    either immediately or like with some autocmd timeoutlen) """


  # # this should go in bufbuffer
  # def on_update(self, status):
  #     previous = self._previous
  #     self._previous = self.text

  #     previous_hit_count = len(self.indices)

  #     if not previous or not self.text.startswith(previous):  # new, restarted or backtracking
  #         self.indices = list(range(self.line_count))       # reset index list
  #         if previous and self.text:                          # if we didnt delete the last char?
  #             self.nvim.call('cursor', [1, self.nvim.current.window.cursor[1]])

  #     elif previous and previous != self.text:                # if query has changed
  #         self.nvim.call('cursor', [1, self.nvim.current.window.cursor[1]])

  #     self.matcher.filter(self.text, self.indices, self._content[:], self.ignorecase)
  #     # ^  weird thing with regex matcher (which unlike others can end up with more chars AND more hits)
  #     # if go eg 'function|return' only adds the return lines once hit backspace...
  #     hit_count = len(self.indices)
  #     if hit_count < 1000:
  #       # syn = syntax_types[SYN_BUFFER] if self.syntax is SYN_BUFFER \
  #                                     # else syntax_types[SYN_FADED]
  #       # hl = self.highlight_groups[syn] + self.matcher.name.capitalize()
  #       hl = 'MetaSearchHit' + self.matcher.name.capitalize()
  #       # need multiple matches. inbetween fuzzy = faded bg of fuzzy fg.  regex wildcards/dots etc, ditto. check denite/fzf sources for how to...
  #       # ALSO: different bg for different words with regular matcher, etc.  ALSO: corresponding highlights in the actual input string.
  #       self.matcher.highlight(self.text, self.ignorecase, hl)  # highlights instances with the appropriate highlighting group
  #     else:
  #         self.matcher.remove_highlight()     #too much, man

  #     if previous_hit_count != hit_count:  # should use more robust check since we can of course end up with same amount, but different hits
  #         assign_content(self.nvim, [self._content[i] for i in self.indices])

  #         if self.signs_enabled:  #remove all signs since they get fucked when we replace text of buffer anyways. Replace dummy
  #             self.nvim.command('sign unplace * buffer=%d' % self.nvim.current.buffer.number)  # no point not clearing since all end up at line 1... but guess theoretically we might want to be able to move along existing signs from other fuckers, sounds far off though so this works for now
  #             self.nvim.command('sign place 666 line=1 name=MetaDummy buffer=%d' %
  #                               self.nvim.current.buffer.number)

  #     time_since_start = time.clock() - self._start_time
  #     try:  self.nvim.call('timer_stop', self.timer_id)
  #     except: pass

  #     if hit_count < 15:
  #         self.update_signs(hit_count)
  #     elif hit_count < self._line_count and time_since_start > 0.035:
  #         sign_limit = min(5 * len(self.text), 25)
  #         self.update_signs(min(hit_count, sign_limit))
  #         self.timer_id = self.nvim.call('timer_start', self.callback_time, 'meta#callback_update')

  #     return super().on_update(status)

