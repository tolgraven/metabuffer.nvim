Metabuffer
==============================================================================

Introduction
-------------------------------------------------------------------------------

Metabuffer is a plugin to source and filter content. What differentiates what
it (doesn't remotely yet) do from the multitude of existing fuzzy-finders and
matchers is that instead of searching for something, then jumping there, we
want to simply pull towards us, aggregate what we are interested in modifying,
and have any changes propagated back to their original locations,
automatically.

Think FZF + NarrowRegion + batshit regex wizardry, on steroids, and super
WYSIWYG and real-time.

Together with new methods of filtering, for example by type (via syntax
highlighting group, so should support everything vim does), and not requiring
(but allowing) one to remembe a bunch of arcane syntax and formulate a query
solely by typing, but equally by 'tapping' things - pointing at them going
filter out all stuff like this (comments, and docstrings, say), require that
('everything else in function bodies') - it aims to not just make finding
easier, but editing too.  Minimizing context switches by not chasing files and
regions within them, but simply pulling up what's relevant, and working on it.
Since a metabuffer, once out of prompt and back in normal mode, is simply a
buffer like any other, all regular editing tools stay available, including
plugins and external ones.

Navigation and refactoring are the obvious applications, but I think this
concept of keeping metadata for each line and keeping track of its origin and
purpose should allow extending the workflow to many types of sources.  Putting
an `ls -la` in a metabuffer, and making modifications, should move the files
correspondingly.  The end product should approach something like a mix between
a regular buffer, fuzzy finder, shell/REPL - and importantly, the latters
output.  All with glorious native syntax highlighting, and extensive
expandability.


Literally all of that is super far off as of now, and currently it mainly
functions as a slightly polished (and also very buggy) version of lambdalisue's
excellent Lista plugin.

Stay tuned and hopefully soon there will be enough functionality available that
it starts making some kind of sense. Maybe.

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
