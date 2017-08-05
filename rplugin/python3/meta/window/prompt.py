from .window import AbstractWindow


class PromptWindow(AbstractWindow):
  """A window acting as a prompt"""
  name = 'promptwindow'


  def __init__(self, nvim, height = 0):
    """Constructor.

    Args:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance
        height (int): initial height of window, 0 = auto
    """
    # XXX question: this just a small thing that we'll put in new prompt class
    # when redesigning it to use a reg buffer/window instead of vim's prompt?
    self.nvim = nvim
    self.nvim.command('botright new')
    self.window = self.nvim.current.window

