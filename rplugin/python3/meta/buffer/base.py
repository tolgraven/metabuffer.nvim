"""Buffer module."""
from abc import ABCMeta, abstractmethod


class AbstractBuffer(metaclass=ABCMeta):
    """An abstract buffer class.

    Attributes:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        nvim.buffer (neovim.Nvim.buffer): A ``neovim.Nvim.buffer`` instance.
    """

    name = 'abstract'

    def __init__(self, nvim, buffer, opts = []):
        """Constructor.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            nvim.buffer (neovim.Nvim): A ``neovim.Nvim.buffer`` instance.
        """
        self.nvim = nvim
        self.buffer = buffer      #nvim buffer object
        self.name = self.nvim.eval('simplify(expand("%:~:."))')
        self.content = list(map(lambda x: ANSI_ESCAPE.sub('', x), self._buffer[:] ))
        self.line_count = len(self.content)
        self.indices = list(range(self.line_count))
        self.bufhidden = self.buffer.options['bufhidden']
        self.syntax = self.buffer.options['syntax']   #all buffers will have a syntax, even if it's "none"
        #for a dummy buffer it will mean the currently active syntax in vim,
        #for a backing buffer it will be its original syntax
        self.vim_id = self.buffer.number

        self.signs = self.nvim.command_output('silent sign place buffer=' + self.nvim.current.buffer.number)


        # #when creating new from scratch
        # self.nvim.command('noautocmd keepjumps enew')
        # self.buffer[:] = text
        #have alt constructor from scratch, provide text contents and whatever non-default opts we want


        # "exceptions" - would be handled through matchers I guess, but easier
        # with like a flag telling the buffer to ignore the operations that 
        # otherwise would occur on it


# Types of buffers:
# - Regular: vim buffer, as normal. A potential source
# - Meta: a vim dummy buffer containing multiple other buffers as its inputs,
# and through then, back-propgating changes to their original location
# - UI: helper buffer containing UI elements, basically to get around vim's
# limitations here (only 2 char sign column, etc). Should be linked with other
# buffers through a metawindow container...

# better to minimize types so that sources is a list by default I guess,
# whether contains one or several
# but guess point is a metabuffer will contain a bunch of instances of its
# relatives... who filter themselves and handle their own shit yeah?

    def __del__(self):
        """nuke self"""
        self.buffer.options['bufhidden'] = 'wipe'
        self.buffer.options['bufoptions'] = 'wipe'
        self.nvim.command('sign unplace * buffer=%d' % self.vim_id)
        # other cleanup and that


    def sign_add(self, signstuff):
      # first like check to see the sign we're adding is actually defined, if not, do it
      # self.nvim.command('sign place ')
      pass

    def sign_delete(self, signstuff):
      # self.nvim.command('sign unplace ')
      pass


    @abstractmethod
    def get_highlight_pattern(self, query):
        """

        Args:

        Returns:
        """
        raise NotImplementedError

    @abstractmethod
    def filter(self, query, indices, candidates, ignorecase):
        """

        Args:

        Returns:
        """
        raise NotImplementedError


