Metabuffer
==============================================================================

Introduction
-------------------------------------------------------------------------------

Metabuffer is a plugin to source and filter content. What differentiates what it (aims to)
do from the multitude of existing fuzzy-finders and matchers is that instead of searching for something,
then jumping there, we want to simply pull towards us, aggregate what we are interested in modifying, 
and have any changes propagated back to their original locations, automatically.

Together with new tools for filtering, for example syntax-based, it aims to not just make finding
what you need easier, but editing too.
And since a metabuffer, once out of prompt and back in normal mode, is simply a buffer like any other,
all regular editing tools stay available.

All that is super far off as of now, and currently it mainly functions as a slightly polished 
(and also very buggy) version of lambdalisue's excellent Lista plugin.

Stay tuned...

Install
-------------------------------------------------------------------------------

Install it with your favorite plugin manager.

```vim
Plug 'tolgraven/metabuffer.nvim'
```


Usage
-------------------------------------------------------------------------------
Execute `:Meta` or `:MetaCursorWord` and use the following builtin mappings





See also
-------------------------------------------------------------------------------
This plugin has partially forked from or inspired by the following plugins.

- lambdalisue/lista.nvim (especially)
- [Shougo/unite.vim](https://github.com/Shougo/unite.vim)
- [osyo-manga/vim-hopping](https://github.com/osyo-manga/vim-hopping)
- [Shougo/denite.nvim](https://github.com/Shougo/denite.nvim)
- [lambdalisue/neovim-prompt](https://github.com/lambdalisue/neovim-prompt)
