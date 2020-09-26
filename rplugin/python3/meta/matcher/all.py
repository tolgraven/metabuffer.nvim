from .base import AbstractMatcher, escape_vim_patterns


class Matcher(AbstractMatcher):
    """An all matcher class for filter candidates."""
    name = 'all'

    def get_highlight_pattern(self, query):
        patterns = map(str.strip, query.split())
        return '\%%(%s\)' % '\|'.join(
            map(escape_vim_patterns, patterns)
        )

    def filter(self, query, indices, candidates, ignorecase):
        patterns = map(str.strip, query.split())
        if ignorecase:
          patterns = map(str.lower, patterns)
          candidates[:] = [cand.lower() for cand in candidates]
        patterns = list(patterns) # cant do inline below. learn python and figure out why!
        indices[:] = [
            i for i in indices
            if all(p in candidates[i] for p in patterns)
        ]
