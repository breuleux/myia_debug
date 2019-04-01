
import os

if os.environ.get('BUCHE'):
    from dbg import do_inject
    from dbg.butest import *
