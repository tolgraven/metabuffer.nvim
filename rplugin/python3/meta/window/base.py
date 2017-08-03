
"""Window module."""
from abc import ABCMeta, abstractmethod


class AbstractWindow(metaclass=ABCMeta):
    """An abstract window class.

    Attributes:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        nvim.buffer (neovim.Nvim.window): A ``neovim.Nvim.window`` instance.
    """

    name = 'abstract'

    def __init__(self, nvim, window, opts = []):
        """Constructor.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            nvim.window (neovim.Nvim): A ``neovim.Nvim.window`` instance.
        """
        self.nvim = nvim
