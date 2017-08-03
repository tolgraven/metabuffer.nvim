from .window import AbstractWindow


class MetaWindow(AbstractWindow):
  """A container window consisting of several linked windows acting in tandem"""
  name = 'metawindow'


  def __init__(self, nvim, window):
    """Constructor.

    Args:
        nvim.window (neovim.Nvim): A ``neovim.Nvim.window`` instance - the master window
    """

