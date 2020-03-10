import neovim
import os

nvim = neovim.attach('socket', path='/tmp/nvimsocketmeta-dev')

import meta
from meta.meta import Meta
# %run './rplugin/python3/meta/__init__.py' # if straight from thing also refreshes code
# meta.start(nvim, [''], 'start')
