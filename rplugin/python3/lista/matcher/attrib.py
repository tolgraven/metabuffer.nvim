
from .base import AbstractMatcher, escape_vim_patterns


class Matcher(AbstractMatcher):
    """A semantic attribute matcher class for filter candidates. Should be
    further subclassed to specific examples of this? Like for example """
    name = 'attrib'

    def get_highlight_pattern(self, query):
        chars = map(escape_vim_patterns, list(query))
        patterns = map(str.strip, query.split())

    def filter(self, query, indices, candidates,):
        patterns = map(str.strip, query.split())

