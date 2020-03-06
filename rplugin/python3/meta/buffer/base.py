"""Buffer module."""
from meta.handle import MetaHandle


class AbstractBuffer(MetaHandle):
  """An abstract buffer class.

  Attributes:
    nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
    nvim.buffer (neovim.Nvim.buffer): A ``neovim.Nvim.buffer`` instance.
    opts (dict): A dictionary containing options to apply on creation
  """

  name = 'abstract'
  syntax_types = ['buffer', 'meta']  # will this ever be the extent of it with # matchadd covering the rest, or can I come up with new categories? there is some way of combining properties of multiple syntax that I read about, look up.
  syntax_type = 'buffer' #temp

  def __init__(self, nvim, buffer, opts = {}):
    """Constructor.
    Args:
      nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
      nvim.buffer (neovim.Nvim): A ``neovim.Nvim.buffer`` instance.
    """
    super().__init__(nvim, buffer, opts) #well gets weird
    self.buffer = self.target

    # "exceptions" - some lines/buffers need to be frozen/unaffected by edits. How best handle?
    # because not just about not propogating back to source, but also (I guess?) instantly reverting edits so they keep showing up the same...


# Types of buffers:
# - Regular: vim buffer, as normal. A potential source
# - Meta: a vim dummy buffer containing multiple other buffers as its inputs,
# and through then, back-propgating changes to their original location
# - UI: helper buffer containing UI elements, basically to get around vim's
# limitations here (only 2 char sign column, etc). Should be linked with other
# buffers through a metawindow container...

# better to minimize types so that sources is a list by default I guess, whether contains one or several
# but guess point is a metabuffer will contain refs to a bunch of instances of its relatives... who filter themselves and handle their own shit yeah?

  def __del__(self):
    """nuke self"""
    # self.buffer.options['bufhidden'] = 'wipe'
    # self.nvim.command('sign unplace * buffer=%d' % self.vim_id)
    # self.nvim.command('bwipe %d' % self.vim_id)  #something like that


  # @syntax_type.setter
  # def syntax_type(self, new_type):
  #   self.syntax_type = new_type




  def sign_add(self, signstuff):
    # first like check to see the sign we're adding is actually defined, if not, do it
    # self.nvim.command('sign place ')
    pass

  def sign_delete(self, signstuff):
    # self.nvim.command('sign unplace ')
    pass


  # def from_lines(self, lines):
  #   self.content = list(map(lambda x: ANSI_ESCAPE.sub('', x), str(lines[:]) ))

