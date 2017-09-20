"""Matcher module."""
from abc import ABCMeta, abstractmethod


ESCAPE_VIM_PATTERN_TABLE = str.maketrans({
    '^': '\\^',
    '$': '\\$',
    '~': '\\~',
    '.': '\\.',
    '*': '\\*',
    '[': '\\[',
    ']': '\\]',
    '\\': '\\\\',
})


class AbstractMatcher(metaclass=ABCMeta):
    """An abstract matcher class.

    Attributes:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
    """

    name = 'abstract'
    also_highlight_per_char = False

    def __init__(self, nvim):
        """Constructor.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        """
        self.nvim = nvim
        self._match_id = None    # type: int
        self._char_match_id = None  # type: int

    def remove_highlight(self):
        """Remove current highlight."""
        if self._match_id:
            self.nvim.call('matchdelete', self._match_id)
            self._match_id = None
        if self._char_match_id:
            self.nvim.call('matchdelete', self._char_match_id)
            self._char_match_id = None


    def highlight(self, query, ignorecase, highlight_group='Title', char_highlight_group='IncSearch'):
        """Highlight ``query``.

        Args:
            query (str): A query string.
            ignorecase (bool): Boolean to indicate ignorecase.
            highlight_group (str): Vim highlight group to use, if not default.
            char_highlight_group (str): Vim highlight group for per-char matching, if not default.
        """
        self.remove_highlight()
        if not query:
            return
        pattern = self.get_highlight_pattern(query)
        self._match_id = self.nvim.call(
            'matchadd',
            highlight_group,
            ('\c' if ignorecase else '\C') + pattern,
            0,
        )
        if self.also_highlight_per_char:
            self._char_match_id = self.nvim.call(
                'matchadd', char_highlight_group,
                str('\|').join(query), 0)

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


def escape_vim_patterns(text):
    """Escape patterh character used in Vim regex.

    Args:
        text (str): A text being escape.

    Returns:
        str: A escaped text.
    """
    return text.translate(ESCAPE_VIM_PATTERN_TABLE)
