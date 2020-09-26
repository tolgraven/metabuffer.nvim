import re
from copy import deepcopy
from .base import AbstractBuffer
from .ui import Buffer as UiBuffer
from meta.sign import Signs, MetaSign


ANSI_ESCAPE = re.compile(r'\x1b\[[0-9a-zA-Z;]*?m')

class Buffer(AbstractBuffer):
  """A vim buffer wrapper backed by other sources
  Will want some specialized types:
  - Very soon something parsing grep output so can replace :Ag with this.
    Dont need fancy super-generic multi-types from start, just something working.
  """
  name = 'meta'

  syntax_types = ['buffer', 'meta']  # will this ever be the extent of it with # matchadd covering the rest, or can I come up with new categories? there is some way of combining properties of multiple syntax that I read about, look up.
  default_opts = {'buflisted': False,
                  'bufhidden': 'hide',
                  'buftype': 'nofile',
                  }  # this is where different types of buffers will diverge I suppose. These only apply for temp kind...
  # nofile/write:	When using ":e bufname" and already editing "bufname" the buffer is
  #               made empty and autocommands are triggered as usual for |:edit|.
  # so for file naming will have to add an instance UID as well so dont overwrite...

  # views = []  # a metabuffer should be able to present the same material with multiple views
  # meta_material = [] # metadata parallel to model source material, start first w linenr thing...
  # inputs = [] # (Meta)Buffers only? or easier also add standalone nvim buf prob..

  def __init__(self, nvim, model = None, opts = {}): # sending a (nvim, not meta) buffer to model. cause seems silly just taking over stuff that's how you break shit
    """Basically all of this should go up AbstractBuffer"""

    self.syntax_type = 'buffer' #temp
    super().__init__(nvim, None, model, [], self.default_opts)
    self._content = list(map(lambda x: ANSI_ESCAPE.sub('', x), self.model[:]))
    # tho the escaping will have to be undone or w/e when comparing/pushing right...
    self._indices = list(range(self.line_count))            #not to change
    self.filtered_indexes = deepcopy(self._indices)

    self.indexbuf = UiBuffer(nvim, self, "indexes", self.default_opts)

    self.has_signs = Signs.buf_has_signs(nvim, self.model)
    if self.has_signs:
      self.signs = Signs(nvim, self.buffer, force=True)
      nvim.current.window.options['signcolumn'] = 'yes' #force signs. but window setting, so b careful...


    self.update()   # or defer but then need to flush manually
    # update also needs to go through views sources etc ask them to try update everything propagating


    # self.sources = [self]         # a list of Buffer objects, together representing the total text content of this dummy buffer
    # self.rank = ranker # steal something from denite since we need to be able to sort, not the text within each source but the sources themselves
    # self.presentation = False        #like for dummy buffers, stuff to change presentation (whitespace, columns etc...) and other minor stuff, without touching original for those operations
    # self.content[:] = self.sources.join('\n')  #cause I guess we don't need/want dedicated setterart from constructor, just add sources and refresh rather?

    # buffer.add_highlight(hl_group, line, col, col_end, src_id) #well random. useful for something i guess.
    # nvim.new_highlight_source()


  def update(self):
    """Has trouble with not being able to change buffer without
    activating? (within running metaprompt)"""
    if self.has_signs: self.signs.refresh()
    super().update() # now not actually filtering when restoring - huh?
    # for v in self.views: v.update()
    # for i in self.inputs: i.update()
    self.indexbuf.update()
    # for f in self.transforms: f(self) # better later if must be pure and yada dada

  @property
  def syntax(self):
    """Return either original (model) buffer syntax, or our special faded
    syntax, depending on settings"""
    if self.syntax_type == 'buffer' and self.model.options['syntax']:
      return self.model.options['syntax']
    else:
      return 'meta'

  def apply_syntax(self, syntax_type = None):
    """try get orig buffer syntax else fallback etc"""
    if syntax_type: self.syntax_type = syntax_type
    self.nvim.command('set syntax=' + self.syntax)  # init at index 0 = buffer, for now. Consistent with the others, but can't be hardset later when more appear

  def step_into(self, source, idx):
    """Navigate into a proper view of a source buffer, which might well not
    yet exist as an actual buffer in case of global grep aggregation stuff.
    So look for existing, else load, yada."""


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

  def indexes_as_content(self):
    self.target[:] = [self.indices[i] for i in range(len(self.indices))]


  def add_view(self):
    """Test"""
    # new_view = MetaBuffer(self.nvim, self.buffer)
    # new_buf =
    # AbstractBuffer.switch_buf(self.nvim, self.buffer)
    # views.append(new_buf)
    # just define something so on update base will shovel something into a buf
    # no extra meta object-whatever. maybe a view class

    # new_view = Buffer(self.nvim, self.buffer)
    # new_view.add_transform(Buffer.indexes_as_content)
    # self.views.append(new_view)
    # f = lambda this: this.target[:] = [this.indices[i] for i in range(len(this.indices))]
    # new_view.add_transform(f)
    # new_view.add_transform(lambda this: this.target[:] = [this.indices[i] for i in range(len(this.indices))])
    # "tell new_view to mirror us, but instead of content, indexes"


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


