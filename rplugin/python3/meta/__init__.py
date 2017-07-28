try:
    import neovim

    @neovim.plugin
    class MetaEntryPoint:
        def __init__(self, nvim):
            self.nvim = nvim

        @neovim.function('_meta_start', sync=True)
        def start(self, args):
            return start(self.nvim, args, False)

        @neovim.function('_meta_resume', sync=True)
        def resume(self, args):
            return start(self.nvim, args, True)

        @neovim.function('_meta_callback_signs', sync=True)
        def callback_signs(self, args):
            return callback_signs(self.nvim, args, True)

except ImportError:
    pass


def start(nvim, args, resume):
    import traceback
    try:
        from .prompt.prompt import STATUS_ACCEPT, STATUS_CANCEL, STATUS_INTERRUPT
        from .meta import Meta, Condition
        if resume and '_meta_context' in nvim.current.buffer.vars:
            context = nvim.current.buffer.vars['_meta_context']
            context['text'] = context['text'] if not args[0] else args[0]
            condition = Condition(**context)
        else:
            condition = Condition(
                text=args[0], caret_locus=0,
                selected_index=nvim.current.window.cursor[0] - 1,
                matcher_index=0, case_index=0, syntax_index=0,
            )
        meta = Meta(nvim, condition)
        status = meta.start()
        nvim.command('redraw')
        if status == STATUS_ACCEPT:
            # nvim.call('cursor', [meta.selected_line, 0])  #doesnt add prev loc to jumplist...
            nvim.command(':' + str(meta.selected_line))
            # other alternative is to set a manual mark m', no downsides?
            nvim.command('normal! zvzz')
            nvim.call('setreg', '/', meta.get_searchcommand())  #populate search reg

        elif status == STATUS_CANCEL:
            nvim.command('echomsg "STATUS_CANCEL"')
            #should restore properly, not modify search reg etc
        elif status == STATUS_INTERRUPT:
            nvim.command('echomsg "STATUS_INTERRUPT"')
            #arfthis will be "normal mode" i guess. leave dummy up...

        nvim.current.buffer.vars['_meta_context'] = meta.store()._asdict()
    except Exception as e:
        from .prompt.util import ESCAPE_ECHO
        nvim.command('redraw!')
        nvim.command('redrawstatus')
        nvim.command('echohl ErrorMsg')
        for line in traceback.format_exc().splitlines():
            nvim.command('echomsg "%s"' % line.translate(ESCAPE_ECHO))
        # nvim.command()  #check if buffer is hanging around, clean it up, etc etc
        # should be generalized as much as possible so that can be used for the meta buffers
