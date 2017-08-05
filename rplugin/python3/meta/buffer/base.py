"""Buffer module."""
from abc import ABCMeta, abstractmethod


class AbstractBuffer(metaclass=ABCMeta):
  """An abstract buffer class.

  Attributes:
    nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
    nvim.buffer (neovim.Nvim.buffer): A ``neovim.Nvim.buffer`` instance.
    opts (dict): A dictionary containing options to apply on creation
  """

  name = 'abstract'

  def __init__(self, nvim, buffer = None, opts = {}):
    """Constructor.

    Args:
      nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
      nvim.buffer (neovim.Nvim): A ``neovim.Nvim.buffer`` instance.
    """
    self.nvim = nvim
    if buffer:
      self.buffer = buffer      #nvim buffer object
    else:
      active = self.nvim.current.buffer
      self.nvim.command('noautocmd keepjumps enew')
      self.buffer = self.nvim.current.buffer
      self.nvim.command('noautocmd keepjumps buffer %d' % active.number)
    self.name = self.buffer.name #full path or name from :file i guess?
    self.name_short = self.name.split('/')[-1]
    self.vim_id = self.buffer.number

    self.content = list(map(lambda x: ANSI_ESCAPE.sub('', x), self.buffer[:] ))
    self.line_count = len(self.content)
    self.indices = list(range(self.line_count))
    self.syntax = self.buffer.options['syntax']   #all buffers will have a syntax, even if it's "none"
    #for a dummy buffer it will mean the currently active syntax in vim,
    #for a backing buffer it will be its original syntax

    self.signs = self.nvim.command_output('silent sign place buffer=' + self.nvim.current.buffer.number)

    # self.buffer[:] = text
    # "exceptions" - some lines/buffers need to be frozen/unaffected by edits. How best handle?
    # because not just about not propogating back to source, but also (I guess?) instantly reverting edits so they keep showing up the same...
    if len(opts): self.opts(opts)

    self.on_init()


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
    self.buffer.options['bufhidden'] = 'wipe'
    self.nvim.command('sign unplace * buffer=%d' % self.vim_id)
    # self.nvim.command('bwipe %d' % self.vim_id)  #something like that


  def sign_add(self, signstuff):
    # first like check to see the sign we're adding is actually defined, if not, do it
    # self.nvim.command('sign place ')
    pass

  def sign_delete(self, signstuff):
    # self.nvim.command('sign unplace ')
    pass

  def opts(self, opts):
    for opt,val in opts.items(): self.buffer.options[opt] = val


  # def from_lines(self, lines):
  #   self.content = list(map(lambda x: ANSI_ESCAPE.sub('', x), str(lines[:]) ))


  @abstractmethod
  def on_init(self):
    """Specific initialization

    Args:

    Returns:
    """
    raise NotImplementedError

  @abstractmethod
  def on_term(self):
    """

    Args:

    Returns:
    """
    raise NotImplementedError

