"""Object creation and entry points for Meta"""
import pynvim
from typing import Optional
import pudb

import logging
logfile = '/Users/tol/.local/share/nvim/meta.log'
level = logging.DEBUG
logging.basicConfig(filename=logfile, level=level)

# for development...
# nvim = pynvim.attach('socket', path='/tmp/nvimsocketmeta')

@pynvim.plugin
class MetaEntryPoint(object):
  # meta = None  #store object
  def __init__(self, nvim):
    self.nvim = nvim
    self.meta = new_instance(nvim) # will have to move a ton out of __init__ tho
    # and thinking ahead of course must support multiple instances

  # the .function ones dont seem to actually export tho? guess that's what the
  # wrapper i nuked was heh
  # allow_newsted=True
  @pynvim.function('MetaStart',  sync=True)
  def start(self, args, force_new=False):
    if force_new and self.meta:
      # first cleanup existing instance?
      self.meta = Meta(self.nvim, setup_state(self.nvim, args))
    self.meta = start(self.nvim, args, 'start', self.meta)
  @pynvim.command('Meta', nargs='?', sync=True, bang=True) #how access bang?kll
  def meta_start(self, args, bang): self.start(args, bang)

  @pynvim.function('MetaResume', sync=True)
  def resume(self, args):       return start(self.nvim, args, 'resume')

  @pynvim.command('MetaSync', nargs='?', sync=False)
  # @pynvim.command('MetaSync', nargs='?', sync=True)
  def meta_sync(self, args):
    """Can now run without first doing start(), tho lots of stuff not
    properly setup..."""
    self.meta = sync(self.nvim, self.meta, args)

  @pynvim.command('MetaPush', nargs='0', sync=False)
  def meta_push(self, args):
    push(self.nvim, self.meta, args)

  @pynvim.function('MetaFinish', sync=True)
  def finish(self, args):       return finish(self.nvim, args)

  @pynvim.function('MetaCallbackSigns', sync=True)
  def callback_signs(self, args): return callback_signs(self.nvim, args)

  @pynvim.command('MetaCursorWord', nargs='?', sync=True)
  def meta_cursor_word(self, args):
    self.start([self.nvim.funcs.expand('<cword>')])

  @pynvim.command('MetaResume', nargs='?', sync=True)
  def meta_resume(self, args):  self.resume(args)
  @pynvim.command('MetaResumeCursorWord', nargs='?', sync=True)
  def meta_resume_cursor_word(self, args):
      self.resume([self.nvim.funcs.expand('<cword>')])

  # @pynvim.autocmd('BufEnter', pattern='*.py', eval='expand("<afile>")', sync=True)
  # def on_bufenter(self, filename): self.nvim.out_write('testplugin is in ' + filename + '\n')

from meta.prompt.prompt import STATUS_ACCEPT, STATUS_CANCEL, STATUS_INTERRUPT, STATUS_PROGRESS, STATUS_PAUSE
from meta.meta import Meta, Condition, default_condition
from meta.buffer.metabuffer import Buffer as MetaBuffer
# from meta.window.metawindow import Window as MetaWindow

def setup_state(nvim, args, mode = 'start') -> Condition:
  if not len(args): args = ['']      # ensure arg[0] exists... <q-args> compat

  if mode == 'resume' and '_meta_context' in nvim.current.buffer.vars:
      context = nvim.current.buffer.vars['_meta_context']
      if args[0]:
        context['text'] = args[0]          # override text state - shouldnt caret pos etc change then too tho
        context['caret_locus'] = len(args[0])
      condition = Condition(**context)
  else:  #fresh start. dont check for 'start' specifically, so an invalid resume request wont fail but simply star from 0
      condition = default_condition(nvim, args[0])   # static fuckers glitchy whether work, why

  return condition

def new_instance(nvim) -> Meta:
  return Meta(nvim, default_condition(nvim))


def start(nvim, args=[''], mode="start", meta=None) -> Optional[Meta]:  # whether to force new meta object or not. reuse curr not working
    """Prob makes sense (unless deving and is broken) trying to stash and reuse
     meta instance rather than recreate each time?"""
    import traceback
    try:
        condition = setup_state(nvim, args, mode)
        meta = meta or Meta(nvim, condition)

        status = meta.start()  # main loop. Here's where we need a 2nd entrypoint that just refreshes... something

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

        elif status is STATUS_INTERRUPT or status is STATUS_PAUSE:                    # <C-c>, NORMAL MODE/ PAUSE. Reset buftype and shit to avoid wiping buffer and allow writing to it -> sync it back
            # doesnt seem to arrive here tho
            nvim.err_write('STATUS_INTERRUPT')
            nvim.command('buffer#') #restore alt view, for now. Tho should handle in main class
                                     # nvim.command('set buftype=')                    # clear buftype (nowrite, nofile...)
            # nvim.command('file metabuffer ' + meta.text)    # Name buffer so can see what we were doing. later will ofc have metaprompt hanging around still, but good either way

            # CONSIDER: change HLsearch highight locally, to match our matchadd? again, always minimize jittery disruptive changes...
            # and then use matchadd as base and set searchcommand to obvs not
            # entire filter query but whatever is deemed most relevant / top of stack like
            # indices[:] = meta.buf.indices                 #grab indices here yeah? set up autocmd to nuke signs once buffer is finally actually killed...

        _wrapup(nvim, meta)
        return meta

    except KeyboardInterrupt:
      nvim.err_write('STATUS_INTERRUPT')
        # gracefully pause yeah
    except Exception as e:
      nvim.command('redraw! | redrawstatus')
      nvim.err_write('%s' % e.__traceback__)
      # .__context__ has other exceptions if multi...

      # nvim.command('redraw! | redrawstatus | echohl ErrorMsg')
      # from meta.prompt.util import ESCAPE_ECHO
      # for line in traceback.format_exc().splitlines():
      #     nvim.command('echomsg "%s"' % line.translate(ESCAPE_ECHO))
      try:
        MetaBuffer.switch_buf(nvim, meta.buf.model)
      except:  #couldnt restore to specific buf, manually try to go to last buf
        nvim.err_write('Couldnt restore buffer')
        # nvim.command('_#')   #alt
    # finally:
    # The exception information is not available to the program during
    # execution of the "finally" clause.
    finally:
        return meta

def _wrapup(nvim, meta):
  # if not meta: return
  # meta.matcher.remove_highlight()                 # Remove temp matcher hl - vim search (if any) takes over
  nvim.command('redraw | redrawstatus')
  _store_vars(nvim, meta)

def _store_vars(nvim, meta):
  save = [['context', meta.store()._asdict()],
          ['indexes', meta.buf.indices],
          ['updates', meta.updates],]
  for var,src in save:
    nvim.current.buffer.vars['_meta_' + var] = src  # sort some dedicated fn tho


def sync(nvim, meta, args) -> Optional[Meta]:
    """Update search query and reflect in open buffer, which is (as before)
    the alt file of our original/model buffer. Store updated query and indices...
    Will want to save each change in a stack so can step view back and forth and not lose track..."""
    if not meta:
      nvim.err_write('No Meta instance')
      return None

    # pudb.set_trace()
    # meta.update_query(args[0]) #set query and save
    meta.query = args[0]
    meta.on_update(STATUS_PROGRESS)
    _store_vars(nvim, meta)
    return meta

    #ersatz main loop...do shit with diff and write n dat

def fetch(nvim, meta, args):
    """Will want something to go other way round too - thinking if do a sync then
    undo to get back to prev state - so figure which events are editing and which
    are to be considered rocknrolling the filter?"""

def push(nvim, meta, args):
    """Push changes in alt buffer back to original, which might also be
    a metabuffer in turn updating children etc.
    FIX: simply by line very limited, will have to create diff so can insert/del lines
    as well. Then must decide what gets anchored where - but prev as anchor sensible"""
    for idx, src_idx in enumerate(meta.buf.indices):
      if meta.buf.model[src_idx] != meta.buf.buffer[idx]:
        meta.buf.model[src_idx] = meta.buf.buffer[idx]
        # meta.buf.push_line(line, txt)
        # nvim.api.buf_set_lines(meta.buf.model.handle, line+1, line+1, False, txt)
    # hmm batching obvs better performance, check whether automatically
    # chunks under hood. Definitely does afa undo history so that's nice!


def get_vim_range(nvim, meta, args):
    """Get range prefix for current filter, for use with external commands.
    Obvs point is not having to bother with such (just edit and push).
    Temp for testing..."""
    pass


def finish(nvim):
    pass
    #cleanup everything...

def callback_signs(nvim):
    nvim.command('echomsg "DEFERRED TIMER HIT YO"')

