
"""Buffer module."""
from abc import ABCMeta, abstractmethod



class AbstractBuffer(metaclass=ABCMeta):
    """An abstract buffer class.

    Attributes:
        nvim.buffer (neovim.Nvim): A ``neovim.Nvim.buffer`` instance.
    """

    name = 'abstract'

    def __init__(self, buffer):
        """Constructor.

        Args:
            nvim.buffer (neovim.Nvim): A ``neovim.Nvim.buffer`` instance.
        """
        self.buffer = buffer
        self.attributes = {[]}    # the relevant options so that any dummy
        # buffers controlling this buffer behave horrectly, and restore all original options properly.
#so it'll be like
        # self.syntax =       #all buffers will have a syntax, even if it's "none"
        # self.vim_id = self.buffer.
                  #for a dummy buffer it will mean the currently active syntax in vim, for a backing buffer it will be its original syntax

        # "exceptions" - would be handled through matchers I guess, but easier
        # with like a flag telling the buffer to ignore the operationw that 
        # otherwise would occur on it

        #have alt constructor from scratch, just send contents and whatever nobn-default opts

# Types of buffers:
# - Regular: vim buffer, as normal. A potential source
# - Dummy: a vim buffer holding text/data from another, with no further
# implications. Basic one would be the scratch copy Lista operates on, when
# it's not wiped on exit - or, now, because it has been paused.
# - Meta: a vim dummy buffer containing multiple other buffers as its inputs,
# and through then, back-propgating changes to their original location


    def text(self, text):
        """Set/get text contents of buffer

        Args:
            text (str): A text string
        """

    @abstractmethod
    def get_highlight_pattern(self, query):
        """Get highlight pattern for ``query``.

        Args:
            query (str): A query string.
            ignorecase (bool): Boolean to indicate ignorecase.

        Returns:
            str: A pattern to highlight.
        """
        raise NotImplementedError

    @abstractmethod
    def filter(self, query, indices, candidates, ignorecase):
        """Filter candidates with query and return indices.

        Args:
            query (str): A query string.
            indices (Sequence[int]): An index list available.
            candidates (Sequence[str]): A candidate list.
            ignorecase (bool): Boolean to indicate ignorecase.

        Returns:
            Sequence[int]: A filtered candidate indices.
        """
        raise NotImplementedError


