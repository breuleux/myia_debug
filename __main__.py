#!/usr/bin/env python

"""Debug Myia

Usage:
  dm <command>
     [-f FUNCTION...] [-a ARG...] [-g...]
     [-t TYPE...]
     [--shapes SHAPE...]
     [-O OPT...]
     [--config FILE...]
     [--pipeline PIP...]
     [--scalar]
     [--no-beautify]
     [--function-nodes]
     [<rest>...]

Options:
  -f --fn FUNCTION...   The function to run.
  -a --args ARG...      Arguments to feed to the function.
  -g                    Apply gradient once for each occurrence of the flag.
  -t --types TYPE...    Types of the arguments.
  --shapes SHAPE...     Shapes of the arguments.
  -c --config FILE...   Use given configuration.
  -O --opt OPT...       Run given optimizations.
  -p --pipeline PIP...  The pipeline to use.
  --scalar              Use the scalar pipeline.
  --no-beautify         Don't beautify graphs.
  --function-nodes      Show individual nodes for functions called.
"""

import operator
from docopt import docopt
from functools import reduce

from myia.debug import traceback
from myia.infer import InferenceError
from myia.opt import lib as optlib
from myia.pipeline import merge

from . import cmd, cfg, typ, steps, do_inject
from .tools import Options, Not


def imp(ref):
    return __import__(ref)


def force_sequence(x, always_wrap=True):
    if isinstance(x, (list, tuple)) and not always_wrap:
        return list(x)
    else:
        return [x]


def resolve(ref, default_modules=[], always_wrap=True, split=True):
    def fsq(x):
        if neg:
            x = Not(x)
        return force_sequence(x, always_wrap)

    def do_all(rs, split=True):
        parts = [resolve(r, default_modules, always_wrap, split=split)
                 for r in rs]
        return reduce(operator.add, parts, [])

    if isinstance(ref, (list, tuple)):
        return do_all(ref)

    if not isinstance(ref, str):
        return fsq(ref)

    neg = False

    if not split:
        refs = [ref]
    elif ';' in ref:
        refs = ref.split(';')
    else:
        refs = ref.split(',')

    if len(refs) > 1:
        return do_all(refs, split=False)

    if ref.startswith('-'):
        ref = ref[1:]
        neg = True

    ref = ref.replace('!', '_bang_')

    if ':' in ref:
        module, field = ref.split(':')
        m = imp(module)
        return fsq(getattr(m, field))

    if default_modules:
        for mod in default_modules:
            _ = object()
            x = getattr(mod, ref, _)
            if x is not _:
                return fsq(x)

    return fsq(eval(ref))


def process_options(options, rest_target):
    if rest_target:
        options[rest_target] += options['<rest>']
        del options['<rest>']

    command, = resolve(options['<command>'],
                       default_modules=[cmd, cfg])

    fns = resolve(options['--fn'],
                  always_wrap=False)
    args = resolve(options['--args'])
    optim = resolve(options['--opt'],
                    default_modules=[optlib, cfg],
                    always_wrap=False)
    pip = resolve(options['--pipeline'],
                  default_modules=[steps, cfg],
                  always_wrap=False)
    types = resolve(options['--types'], [typ])
    shapes = resolve(options['--shapes'], [typ])
    return {
        **options,
        'command': command,
        'fns': fns,
        'args': args,
        'opts': optim,
        'pipeline': pip,
        'types': types,
        'shapes': shapes,
        'grad': options['-g'],
        'options': options,
    }


def resolve_options(*option_dicts,
                    read_argv=True,
                    read_config=True,
                    rest_target='--fn'):
    options = {}
    for o in option_dicts:
        options = merge(options, o)

    if read_argv:
        options = merge(options, docopt(__doc__))

    if read_config:
        while True:
            configs = resolve(options['--config'],
                              default_modules=[cfg],
                              always_wrap=False)
            options['--config'] = []
            if not configs:
                break
            for config in configs:
                options = merge(config, options)

    return options


def main(*option_dicts, read_argv=True, read_config=True, rest_target='--fn'):
    options = resolve_options(*option_dicts,
                              read_argv=read_argv,
                              read_config=read_config,
                              rest_target=rest_target)
    options = process_options(options, rest_target)
    try:
        options['command'](Options(options))
    except InferenceError:
        raise
    except Exception as e:
        buche(e)


if __name__ == '__main__':
    main()
