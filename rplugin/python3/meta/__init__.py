try:
    import neovim

    @neovim.plugin
    class MetaEntryPoint:
        def __init__(self, nvim): self.nvim = nvim

        @neovim.function('_meta_start', sync=True)
        def start(self, args): return start(self.nvim, args, 'start')

        @neovim.function('_meta_resume', sync=True)
        def resume(self, args): return start(self.nvim, args, 'resume')

        @neovim.function('_meta_sync', sync=True)
        # def sync(self, args): return start(self.nvim, args, 'sync')
        def sync(self, args): return sync(self.nvim, args)

        @neovim.function('_meta_finish', sync=True)
        def finish(self, args): return finish(self.nvim, args)

        @neovim.function('_meta_callback_signs', sync=True)
        def callback_signs(self, args): return callback_signs(self.nvim, args)

except ImportError:
    pass


def start(nvim, args, mode):
    import traceback
    try:
        from .prompt.prompt import STATUS_ACCEPT, STATUS_CANCEL, STATUS_INTERRUPT
        from .meta import Meta, Condition
        if mode is 'resume' and '_meta_context' in nvim.current.buffer.vars:
            context = nvim.current.buffer.vars['_meta_context']
            if args[0]: context['text'] = args[0]
            condition = Condition(**context)
        elif mode is 'start':  #fresh start
            locus = len(args[0]) if args[0] else 0
            condition = Condition(
                text=args[0], caret_locus=locus,
                selected_index=nvim.current.window.cursor[0] - 1,
                matcher_index=0, case_index=0, syntax_index=0, restored=False,
            )
        elif mode is 'sync':  #from bufwrite autocmd
            indices = nvim.current.buffer.vars['_meta_indices']
            #do shit with diff and write n dat
        meta = Meta(nvim, condition)
        status = meta.start()  #main loop. Prob rename from 'start' to 'run', no?
        if status is STATUS_ACCEPT or STATUS_CANCEL:
            nvim.command('sign unplace * buffer=%d' % nvim.current.buffer.number)
            nvim.command('noautocmd keepjumps %dbuffer' % meta.get_origbuffer().number)

        if status is STATUS_ACCEPT:  # <CR>
            # nvim.call('cursor', [meta.selected_line, 0])  #doesnt add prev loc to jumplist...
            nvim.command(':' + str(meta.selected_line))
            nvim.command('normal! zv')  #open any folds after jumping
            # XXX try to land with cursor on same physical line as were on, to again minimize jumpery
            nvim.call('setreg', '/', meta.get_searchcommand())  #populate search reg
            nvim.command('normal! n')  #put cursor at start of searched-for word
            # nvim.command('nohlsearch')  #clear hl

        elif status is STATUS_CANCEL:  # <Esc>
            pass
            # nvim.command('echomsg "STATUS_CANCEL"') #should restore proper properly, not modify search reg etc

        elif status is STATUS_INTERRUPT:  # <C-c>
            # nvim.command('echomsg "STATUS_INTERRUPT"') #NORMAL MODE/ PAUSE. Reset buftype and shit to avoid wiping buffer and allow writing to it -> sync it back
            nvim.command('set buftype=')
            nvim.command('file metabuffer ' + meta.text)  #name buffer so can see what we were doing. later will ofc have metaprompt hanging around still, but good either way
            # CONSIDER: change HLsearch highight locally, to match our matchadd? again, always minimize jittery disruptive changes...
            # and then use matchadd as base and set searchcommand to obvs not
            # entire filter query but whatever is deemed most relevant / top of stack like

            #grab indices here yeah?
            # indices[:] = meta.get_indices()

            # set up autocmd to nuke signs once buffer is finally actually killed...

        nvim.command('redraw')

        nvim.current.buffer.vars['_meta_context'] = meta.store()._asdict()
    except Exception as e:
        from .prompt.util import ESCAPE_ECHO
        nvim.command('redraw! | redrawstatus | echohl ErrorMsg')
        for line in traceback.format_exc().splitlines():
            nvim.command('echomsg "%s"' % line.translate(ESCAPE_ECHO))

        try: nvim.command('noautocmd keepjumps %dbuffer' % meta.get_origbuffer().number)
        except: nvim.command('bnext')  #couldnt restore to specific buf, manually try to go to last buf
        # for now, just restore orig buffer same as on regular termination
        # should be generalized as much as possible so that can be used for the meta buffers


def sync(self, nvim):
    pass
    #ersatz main loop...

def finish(self, nvim):
    pass
    #cleanup everything...

def callback_signs(self, nvim):
    nvim.command('echomsg "DEFERRED TIMER HIT YO"')

