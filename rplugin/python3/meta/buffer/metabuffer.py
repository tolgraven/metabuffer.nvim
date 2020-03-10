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

    model = model_buffer or nvim.current.buffer             #or can we set inn arg
    Buffer.switch_buf(nvim, model)
    self.name = nvim.eval('simplify(expand("%:~:."))')      #need override super which fetches from target.name?

    self._content = list(map(lambda x: self.ANSI_ESCAPE.sub('', x), model[:]))
    self._indices = list(range(self.line_count))            #not to change
    self.filtered_indexes = deepcopy(self._indices)

    super().__init__(nvim, Buffer.new(nvim), model, opts)   # create new buf, pass it up

    self.signs = self.nvim.command_output('silent sign place buffer=%d' % self.model.number)
    self.has_signs = True if len(self.signs) > 2 else False

    self.update()   # or defer?


  def on_init(self):
    pass
    # self.sources = [self]         # a list of Buffer objects, together representing the total text content of this dummy buffer
    # self.rank = ranker # steal something from denite since we need to be able to sort, not the text within each source but the sources themselves
    # self.presentation = False        #like for dummy buffers, stuff to change presentation (whitespace, columns etc...) and other minor stuff, without touching original for those operations
    # self.content[:] = self.sources.join('\n')  #cause I guess we don't need/want dedicated setterart from constructor, just add sources and refresh rather?

  def on_term(self):
    pass

  @property
  def name_short(self): return self.name.split('/')[-1]

  @property
  def content(self):    return self._content
  @property
  def line_count(self): return len(self.content)
  @property
  def indices(self):    return self.filtered_indexes
  @property
  def all_indices(self): return self._indices

  def source_line_nr(self, index):
    """Skip error checking right now so can se where goes wrong"""
    # if index >= len(self.indices): index = -1
    # return self.indices[index] + 1
    if len(self.indices):
      try:
        return self.indices[index] + 1
      except IndexError:
        return None
        # return index
    else:
      return None

  def closest_index(self, line_nr, attempt_true_index=True):
    """For current (filtered) indexes, get matching index if available, else
    the one nearest given line_nr.
    Which should actually also be an index because we're looking up indexes dumbo."""
    index = None
    if attempt_true_index:
      try:  index = self.indices.index(line_nr)
      except ValueError: pass # line filtered out, find closest. prepare for awful algo!
    return index if index != None else self._closest_index(line_nr)


  def _closest_index(self, line_nr):
    for idx in range(len(self.indices)):
      if self.indices[idx] > line_nr:
        idxs = max(idx-1, 0), idx
        dist = [abs(line_nr - line) for line in [self.indices[i] for i in idxs]]
        return idxs[0] if dist[0] < dist[1] else idxs[1]
    return -1       # max idx


  def run_filter(self, matcher, query, ignorecase, run_clean = False):
    if run_clean: self.reset_filter() # new, restarted or backtracking

    matcher.filter(query,
                   self.filtered_indexes,   # .filtered_indexes bc fn is side-effecting, .indices is getter...
                   self.content[:],
                   ignorecase) # ^  weird thing with regex matcher (which unlike others can end up with more chars AND more hits) if go eg 'function|return' only adds the return lines once hit backspace...
    # ^ the horror!! fix this uncouth unpure monstrosity. don't change content in place, return new...
    # also remember if need to look through .indices many times, make a set copy and do it on that for constant time.
    if len(self.indices) < 1000:
      matcher.highlight(query, ignorecase)        # highlights instances with the appropriate highlighting group
    else:
      matcher.remove_highlight()                  #too much, man. better if it resigns to just hl currently visible tho...


  def reset_filter(self):
    """Reset filtered indexes to original (which might later be pre-filtered, tho...)"""
    self.filtered_indexes = deepcopy(self._indices)

  @property
  def syntax(self):
    """Return either original (model) buffer syntax, or our special faded
    syntax, depending on settings"""
    if self.syntax_type is 'buffer' and self.model.options['syntax']:
      return self.model.options['syntax']
    else:
      return 'meta'

  def update(self):
    """update shown content off any filter. but need further sep, have two
    Buffers for available vs. displayed content, then keep taking that concept further"""
    viewinfo = self.nvim.call('winsaveview')  # save where view centered etcetc. Not always ideal when filtering takes us off-center
    self.push_opt('modifiable', True)
    self.buffer[:] = [self.content[i] for i in self.filtered_indexes] # does it run loop and then call w final result or update incr? def need former for performance.
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


