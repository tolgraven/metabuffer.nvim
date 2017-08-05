from .window import AbstractWindow


class MetaWindow(AbstractWindow):
  """A container window potentially consisting of several linked windows acting in tandem"""
  name = 'metawindow'


  def __init__(self, nvim, window):
    """Constructor.

    Args:
        nvim.window (neovim.Nvim): A ``neovim.Nvim.window`` instance - the master window
    """
    #grab below from passed window that we're taking over and eventually restoring.
    foldcolumn = self.window.options['foldcolumn']
    number = self.window.options['number']
    relativenumber = self.window.options['relativenumber']
    wrap = self.window.options['wrap']
    win_opts = {'spell': False, 'foldenable': False, 'foldcolumn': foldcolumn,
                'colorcolumn': '', 'cursorline': True, 'cursorcolumn': False,
                'wrap': wrap, 'relativenumber': relativenumber, 'number': number,
                'conceallevel': conceallevel, 
                }


  def __del__(self):
    """Destructor. Nuke any extra windows. Restore orig window properties."""

