from .base import AbstractMatcher, escape_vim_patterns

class GenericMatcher(AbstractMatcher):
    """Generic matcher class for filter candidates.
    Ideas are I guess:
      -Not (necessarily) regex/pattern based, or built to create highlight...
      -Should be able to easily adapt existing these sorts of thigns
      -Maybe even like "send text through this pipeline, "
      -Or a completely manual list of indexes by whatever source (like a 'match all
      lines' to temp full view without dropping rest of query)
      -Or opposite, "match none" or whatever
      -
      -
      """
    name = 'generic'

    def get_highlight_pattern(self, query):

    def filter(self, query, indices, candidates,):

