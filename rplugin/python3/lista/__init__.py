try:
    import neovim

    @neovim.plugin
    class ListaEntryPoint:
        def __init__(self, nvim):
            self.nvim = nvim

        @neovim.function('_lista_start', sync=True)
        def start(self, args):
            return start(self.nvim, args, False)

        @neovim.function('_lista_resume', sync=True)
        def resume(self, args):
            return start(self.nvim, args, True)

        @neovim.function('_lista_callback_signs', sync=True)
        def callback_signs(self, args):
            return callback_signs(self.nvim, args, True)

except ImportError:
    pass


def start(nvim, args, resume):
    import traceback
    try:
        from .prompt.prompt import STATUS_ACCEPT
        from .lista import Lista, Condition
        if resume and '_lista_context' in nvim.current.buffer.vars:
            context = nvim.current.buffer.vars['_lista_context']
            context['text'] = context['text'] if not args[0] else args[0]
            condition = Condition(**context)
        else:
            condition = Condition(
                text=args[0],
                caret_locus=0,
                selected_index=nvim.current.window.cursor[0] - 1,
                matcher_index=0,
                case_index=0,
                syntax_index=0,
            )
        lista = Lista(nvim, condition)
        status = lista.start()
        # nvim.command('redraw!')
        nvim.command('redraw')
        if status == STATUS_ACCEPT:
            # nvim.call('cursor', [lista.selected_line, 0])
            nvim.call('normal! ' + lista.selected_line + 'gg')
            # other alternative is to set a manual mark m', no downsides
            # as far as i can tell but will have to explore
            nvim.command('normal! zvzz')
            nvim.call(lista.get_searchcommand())

        elif status == STATUS_CANCEL:
          #la
        elif status == STATUS_INTERRUPT:
          #la

        nvim.current.buffer.vars['_lista_context'] = lista.store()._asdict()
    except Exception as e:
        from .prompt.util import ESCAPE_ECHO
        # still need to clean up hey...  on throw/crasch it still mostly ends up with
        # a fucked dangling scratch buffer occupying the window
        nvim.command('redraw!')
        nvim.command('redrawstatus')
        nvim.command('echohl ErrorMsg')
        for line in traceback.format_exc().splitlines():
            nvim.command('echomsg "%s"' % line.translate(ESCAPE_ECHO))
        # nvim.command()  #check if buffer is hanging around, clean it up, etc etc
        # should be generalized as much as possible so that can be used for the meta buffers
