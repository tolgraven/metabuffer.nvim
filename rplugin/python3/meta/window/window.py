from .window import AbstractWindow


class Window(AbstractWindow):
  """A vim window"""
  name = 'window'

  def __init__(self, nvim, window):
    """Constructor.

    Args:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance
        nvim (neovim.Nvim.window): A ``neovim.Nvim.window`` instance
    """
