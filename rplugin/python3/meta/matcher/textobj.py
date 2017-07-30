from .base import AbstractMatcher, escape_vim_patterns

class Matcher(AbstractMatcher):
    """A textobj-based matcher class for filter candidates.
       Usable with larger user-textobjs"""
    name = 'textobj'

    def get_highlight_pattern(self, query):
        # chars = map(escape_vim_patterns, list(query))
        # patterns = map(str.strip, query.split())

    def filter(self, query, indices, candidates,):
        # patterns = map(str.strip, query.split())

