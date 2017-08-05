import re
from .base import AbstractMatcher, escape_vim_patterns
from .util import split_input, convert2regex_pattern

class Matcher(AbstractMatcher):
    """A regex matcher class for filter candidates."""
    name = 'regex'

    def get_highlight_pattern(self, query):
      return convert2regex_pattern(query)


    def filter(self, query, indices, candidates, ignorecase):
        for pattern in split_input(query):
            try:
                p = re.compile(pattern, flags=re.IGNORECASE
                               if ignorecase else 0)
            except Exception:
                return

            indices[:] = [                         
                i for i in indices                
                if p.search(candidates[i]) 
            ]                                     
