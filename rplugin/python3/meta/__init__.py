try:
    import pynvim

    @pynvim.plugin
    class MetaEntryPoint(object):
        def __init__(self, nvim): self.nvim = nvim

        # @pynvim.function('_meta_start', sync=True, eval=None)
        @pynvim.function('meta_start', sync=True)
        def start(self, args): return start(self.nvim, args, 'start')

        @pynvim.function('meta_resume', sync=True)
        def resume(self, args): return start(self.nvim, args, 'resume')

        @pynvim.function('meta_sync', sync=True)
        def sync(self, args): return sync(self.nvim, args)

        @pynvim.function('meta_finish', sync=True)
        def finish(self, args): return finish(self.nvim, args)

        @pynvim.function('meta_callback_signs', sync=True)
        def callback_signs(self, args): return callback_signs(self.nvim, args)

        @pynvim.command('Meta', nargs='?', sync=True)
        def meta_start(self, args): self.start(args)
        @pynvim.command('MetaCursorWord', nargs='?', sync=True)
        def meta_cursor_word(self, args):
          self.start([self.nvim.funcs.expand('<cword>')])

        @pynvim.command('MetaResume', nargs='?', sync=True)
        def meta_resume(self, args): self.resume(args)
        @pynvim.command('MetaResumeCursorWord', nargs='?', sync=True)
        def meta_resume_cursor_word(self, args):
          self.resume([self.nvim.funcs.expand('<cword>')])

except ImportError:
    pass
# for plugin developmnt:
# import neovim
# import os
# nvim = neovim.attach('socket', path='/tmp/nvimsocketmeta-dev')
#
# %run './rplugin/python3/meta/__init__.py'   # also refreshes code
# start(nvim, [], 'start')

def start(nvim, args, mode):
    import traceback
    try:
        from meta.prompt.prompt import STATUS_ACCEPT, STATUS_CANCEL, STATUS_INTERRUPT
        from meta.meta import Meta, Condition, default_condition   # Condition being engrish for State
        from meta.buffer.metabuffer import Buffer as MetaBuffer
        from meta.window.metawindow import Window as MetaWindow

        if not len(args): args = ['']      # eh <q-args> compat test ...

        if mode is 'resume' and '_meta_context' in nvim.current.buffer.vars:
            context = nvim.current.buffer.vars['_meta_context']
            if args[0]:
              context['text'] = args[0]          # override text state - shouldnt caret pos etc change then too tho
              context['caret_locus'] = len(args[0])
            condition = Condition(**context)
        else:  #fresh start. dont check for 'start' specifically, so an invalid resume request wont fail but simply star from 0
            condition = default_condition(nvim, args[0])   # static fuckers glitchy whether work, why

        meta = Meta(nvim, condition)
        status = meta.start()  # main loop. Prob rename from 'start' to 'run', no?

        if status is STATUS_ACCEPT or STATUS_CANCEL:        # Common stuff
            # meta.matcher.remove_highlight()                 # Remove temp matcher hl - vim search (if any) takes over
            nvim.command('sign unplace * buffer=%d' % nvim.current.buffer.number)
            MetaBuffer.switch_buf(nvim, meta.buf.model)

        if status is STATUS_ACCEPT:                         # <CR>
            meta.win.set_row(meta.selected_line, addjump=True)  # Jump to selected line
            nvim.command('normal! zv')                      # Open any folds after jumping
            # TODO try to land with cursor on same physical line as we were on while inside, to again minimize jumpery
            try:        #XXX still get some regex stuff giving matches but not back in vim. also crashing.
              if meta.vim_query:                             # Might not have made a search
                nvim.funcs.setreg('/', meta.vim_query)        # Populate search reg, but don't activate search
                # nvim.command('/%s' % meta.vim_query)        # Search - skips over first hit...
                # nvim.command('normal! n')                   # Activate search / put cursor at start of searched-for word - XXX skips to next line instead if already on it...
            except: pass                                    # No match - prob ok

            # nvim.command('nohlsearch')  #clear hl. maybe after a delay.. def goes for our filter stuff - want to be able to keep it or not but
                                          # must hook into whatever autocmd or something to get rid of it?  nohlsearch I suppose.

        elif status is STATUS_CANCEL:                       # <Esc>, should restore proper properly, not modify search reg etc
            pass
            # nvim.command('echomsg "STATUS_CANCEL"')

        elif status is STATUS_INTERRUPT:                    # <C-c>, NORMAL MODE/ PAUSE. Reset buftype and shit to avoid wiping buffer and allow writing to it -> sync it back
            nvim.command('echomsg "STATUS_INTERRUPT"')
            # nvim.command('set buftype=')                    # clear buftype (nowrite, nofile...)
            # nvim.command('file metabuffer ' + meta.text)    # Name buffer so can see what we were doing. later will ofc have metaprompt hanging around still, but good either way

            # CONSIDER: change HLsearch highight locally, to match our matchadd? again, always minimize jittery disruptive changes...
            # and then use matchadd as base and set searchcommand to obvs not
            # entire filter query but whatever is deemed most relevant / top of stack like
            # indices[:] = meta.buf.indices                 #grab indices here yeah? set up autocmd to nuke signs once buffer is finally actually killed...

    except Exception as e:
        try:
          MetaBuffer.switch_buf(nvim, meta.model_buf)
        except:  #couldnt restore to specific buf, manually try to go to last buf
          nvim.command('echomsg "Couldnt restore buffer"')
           # nvim.command('_#')   #alt

        nvim.command('redraw! | redrawstatus | echohl ErrorMsg')
        from meta.prompt.util import ESCAPE_ECHO
        for line in traceback.format_exc().splitlines():
            nvim.command('echomsg "%s"' % line.translate(ESCAPE_ECHO))

    finally:
        meta.matcher.remove_highlight()                 # Remove temp matcher hl - vim search (if any) takes over
        nvim.command('redraw')
        save = [['context', meta.store()._asdict()],
                ['indexes', meta.buf.indices],
                ['updates', meta.updates],]
        for var,src in save:
          nvim.current.buffer.vars['_meta_' + var] = src  # sort some dedicated fn tho


def sync(self, nvim):
    indices = nvim.current.buffer.vars['_meta_indices']
    #ersatz main loop...do shit with diff and write n dat
    # pass

def finish(self, nvim):
    pass
    #cleanup everything...

def callback_signs(self, nvim):
    nvim.command('echomsg "DEFERRED TIMER HIT YO"')

