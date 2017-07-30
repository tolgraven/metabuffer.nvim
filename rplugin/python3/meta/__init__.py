try:
    import neovim

    @neovim.plugin
    class MetaEntryPoint:
        def __init__(self, nvim):
            self.nvim = nvim

        @neovim.function('_meta_start', sync=True)
        def start(self, args):
            return start(self.nvim, args, 'start')

        @neovim.function('_meta_resume', sync=True)
        def resume(self, args):
            return start(self.nvim, args, 'resume')

        @neovim.function('_meta_sync', sync=True)
        def sync(self, args):
            return start(self.nvim, args, 'sync')

        @neovim.function('_meta_callback_signs', sync=True)
        def callback_signs(self, args):
            return callback_signs(self.nvim, args)

except ImportError:
    pass


def start(nvim, args, mode):
    import traceback
    try:
        from .prompt.prompt import STATUS_ACCEPT, STATUS_CANCEL, STATUS_INTERRUPT
        from .meta import Meta, Condition
        if mode == 'resume' and '_meta_context' in nvim.current.buffer.vars:
            context = nvim.current.buffer.vars['_meta_context']
            # context['text'] = context['text'] if not args[0] else args[0]
            if args[0]:
              context['text'] = args[0]
            condition = Condition(**context)
        elif mode == 'start':  #fresh start
            locus = len(args[0]) if args[0] else 0
            condition = Condition(
                text=args[0], caret_locus=locus,
                selected_index=nvim.current.window.cursor[0] - 1,
                matcher_index=0, case_index=0, syntax_index=0, restored=False,
            )
        elif mode == 'sync':  #from bufwrite autocmd
            indices = nvim.current.buffer.vars['_meta_indices']
            #do shit with diff and write n dat
        meta = Meta(nvim, condition)
        status = meta.start()  #main loop. Prob rename from 'start' to 'run', no?

        nvim.command('redraw')
        if status == STATUS_ACCEPT:
            # nvim.command('noautocmd keepjumps %dbuffer' % meta._buffer.number)
            nvim.command('noautocmd keepjumps %dbuffer' % meta.get_origbuffer().number)
            # nvim.call('cursor', [meta.selected_line, 0])  #doesnt add prev loc to jumplist...
            nvim.command(':' + str(meta.selected_line))
            # nvim.command('normal! zvzz')
            nvim.call('setreg', '/', meta.get_searchcommand())  #populate search reg
            nvim.command('normal! n')  #put cursor at start of searched-for word
            # nvim.command('nohlsearch')  #clear hl

        elif status == STATUS_CANCEL:
            nvim.command('echomsg "STATUS_CANCEL"') #should restore proper properly, not modify search reg etc
            nvim.command('noautocmd keepjumps %dbuffer' % meta.get_origbuffer().number)
        elif status == STATUS_INTERRUPT:
            nvim.command('echomsg "STATUS_INTERRUPT"') #NORMAL MODE/ PAUSE. Reset buftype and shit to avoid wiping buffer and allow writing to it -> sync it back
            nvim.command('set buftype=')
            #grab indices here yeah?
            indices[:] = meta.get_indices()

        nvim.current.buffer.vars['_meta_context'] = meta.store()._asdict()
    except Exception as e:
        from .prompt.util import ESCAPE_ECHO
        nvim.command('redraw!')
        nvim.command('redrawstatus')
        nvim.command('echohl ErrorMsg')
        for line in traceback.format_exc().splitlines():
            nvim.command('echomsg "%s"' % line.translate(ESCAPE_ECHO))

        try:
            nvim.command('noautocmd keepjumps %dbuffer' % meta.get_origbuffer().number)
        finally:
            nvim.command('bp')  #couldnt restore to specific buf, manually try to go to last buf
        # for now, just restore orig buffer same as on regular termination
        # should be generalized as much as possible so that can be used for the meta buffers

def callback_signs(self, nvim):
    nvim.command('echomsg "DEFERRED TIMER HIT YO"')

