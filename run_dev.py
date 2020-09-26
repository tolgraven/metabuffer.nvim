import pynvim
import os
import pudb
# from meta import start, sync, push, MetaEntryPoint
# from meta import MetaEntryPoint, sync
from meta import *
# from meta.meta import *

nvim = pynvim.attach('socket', path='/tmp/nvimsocketmeta-dev')
cond = default_condition(nvim, 'def')
pudb.set_trace(paused=False)    # attach but dont break
import signal
pudb.set_interrupt_handler(signal.SIGTSTP)    # fix so can trigger by ctrl-z?

# m = Meta(nvim, cond)
# m.start()
# should use common entrypoint tho...
mep = MetaEntryPoint(nvim)
# sync(nvim, mep.meta, 'self')
# sync(nvim, mep.meta)

# %run './rplugin/python3/meta/__init__.py' # if straight from thing also refreshes code
# meta.start(nvim, [''], 'start')
