import re
from .base import AbstractMatcher, escape_vim_patterns


class Matcher(AbstractMatcher):
    """A fuzzy matcher class for filter candidates."""
    name = 'fuzzy'
    also_highlight_per_char = True # tbh reg hl completely disappears then...

    def _pat(self, pat, escape_by, query):
        chars = map(escape_by, list(query))
        chars = map(lambda x: pat % (x, x), chars)
        return ''.join(chars)


    def get_highlight_pattern(self, query):
        hi_pat = '%s[^%s]\\{-}'
        return self._pat(hi_pat, escape_vim_patterns, query)

    def filter(self, query, indices, candidates, ignorecase):
        filt_pat = '%s[^%s]*?'
        pattern = self._pat(filt_pat, re.escape, query)
        p = re.compile(pattern, flags=re.IGNORECASE if ignorecase else 0)

        indices[:] = [i for i in indices if p.search(candidates[i])]

