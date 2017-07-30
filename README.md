Metabuffer
==============================================================================

Introduction
-------------------------------------------------------------------------------

Metabuffer is a plugin to source and filter content. The special trick (not yet)
up its sleeve, compared to the multitude of existing fuzzy-finders, is
that instead of simply search, jump, continue as normal, we want to stay where
we are, simply pull things towards us, edit, and have any changes propagated
back to their original locations, automatically.

Think FZF + NarrowRegion + batshit regex wizardry, on steroids, but super
WYSIWYG and real-time.

Add novel ways of filtering, for example by type (syntax def based),
indentation, proximity to other match, textobjs, and not requiring (but
certainly allowing) a bunch of arcane typed syntax, but equally 'tapping'
things - pointing going 'filter out all stuff like this' (comments and
docstrings, say), 'require that' (all lines between term x and the next line
not further indented, perhaps) - it aims to not just make finding easier, but
editing moreso.  Minimizing context switches by not chasing files and the
regions within them, but simply pulling up what's relevant, and working on it.
Since a metabuffer at its core is not a specific plugin layer or blocking
prompt but simply a vim buffer like any other, all regular editing tools stay
available, including other plugins and external unix shit.

Navigation and refactoring are the obvious applications, but I think this
concept of keeping metadata for each line and keeping track of their origin and
vertical resize 82purpose should allow extending the workflow to many types of
sources.  Running `ls -la` to a metabuffer (like `read` into any buffer), and
making modifications, ought to move files and change permissions
correspondingly. Echoing a var then modifying the output could change the var.
More general, have your shell output from a neovim terminal or tmux pane routed
through a metabuffer and instead of scrolling up or searching back, reduce your
entire history to instantly see when exactly you ran cmd foo in dir bar.

The end product should approach something like a regular buffer, potentially
fed by any given number of buffers, files, grep results, other daisy-chained
already-filtered metabuffers... shells or REPL commands, and their output,
filtered by a matcher that understands more than just words.


Except like, it won't be totally overwhelming and stupid, I hope.



All with glorious native syntax highlighting, and extensive expandability.


Literally all of that is super far off as of now, and currently it mainly
functions as a slightly polished and pretty (and also buggy) version of
lambdalisue's excellent Lista plugin, which it's forked from and from which
these over-the-top ideas started to grow.

Stay tuned and hopefully soon there will be enough functionality available that
I can start showing what I mean.


Differences from Lista currently:
- Supports (and runs by default) not a faded-out syntax when filtering, but
	that of the original file. Very nice looking and again, preserving the
	original context as much as possible. Can be switched on the fly.
- Lands on searched-for match instead of just same line
- Set jumpmark so you can get back where you were after a search
- Basic support for showing the line number for each hit in the sign column
- * Sign column is both sluggish and limited, so this kind of thing will later
	be handled by putting metabuffers in "metawindows", splitting up the display
	in serveral scroll-linked windows, acting as one and capable of showing
	additional information / metadata on either side

Install
-------------------------------------------------------------------------------

Install it with your favorite plugin manager.

```vim Plug 'tolgraven/metabuffer.nvim' ```


Usage
-------------------------------------------------------------------------------
Execute `:Meta` or `:MetaCursorWord` and use the following builtin mappings


See also
-------------------------------------------------------------------------------
This plugin has forked from or been inspired by the following plugins.

- [lambdalisue/lista.nvim](https://github.com/Shougo/denite.nvim)
- [Shougo/denite.nvim](https://github.com/Shougo/denite.nvim)
- [lambdalisue/neovim-prompt](https://github.com/lambdalisue/neovim-prompt)
