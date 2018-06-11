#!/usr/bin/env python

"""Debug Myia

Usage:
  dm <command>
     [-f FUNCTION...] [-a ARG...] [-g...]
     [-t TYPE...]
     [-O OPT...]
     [--config FILE...]
     [<rest>...]

Options:
  -f --fn FUNCTION...   The function to run.
  -a --args ARG...      Arguments to feed to the function.
  -g                    Apply gradient once for each occurrence of the flag.
  -t --types TYPE...    Types of the arguments.
  -c --config FILE...   Use given configuration.
  -O --opt OPT..        Run given optimizations.
"""

import operator
from docopt import docopt
from functools import reduce

from myia.opt import lib as optlib

from . import cmd, cfg, typ, do_inject
from .tools import Options


def imp(ref):
    return __import__(ref)


def force_sequence(x, always_wrap=True):
    if isinstance(x, (list, tuple)) and not always_wrap:
        return list(x)
    else:
        return [x]


def resolve(ref, default_modules=[], always_wrap=True):
    def fsq(x):
        return force_sequence(x, always_wrap)

    def do_all(rs):
        parts = [resolve(r, default_modules, always_wrap) for r in rs]
        return reduce(operator.add, parts, [])

    if isinstance(ref, (list, tuple)):
        return do_all(ref)

    if not isinstance(ref, str):
        return fsq(ref)

    refs = ref.split(',')
    if len(refs) > 1:
        return do_all(refs)

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
        else:
            raise Exception(f'Could not resolve reference: {ref}')

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
    types = resolve(options['--types'], [typ])
    return {
        'command': command,
        'fns': fns,
        'args': args,
        'opts': optim,
        'types': types,
        'grad': options['-g'],
        'options': options
    }


def merge_options(d1, d2):
    rval = {}
    keys = set(d1.keys()) | set(d2.keys())
    for k in keys:
        if k not in d1:
            rval[k] = d2[k]
        elif isinstance(d1[k], list):
            rval[k] = d1.get(k, []) + d2.get(k, [])
        else:
            rval[k] = d2.get(k, None) or d1.get(k, None)
    return rval


def resolve_options(*option_dicts,
                    read_argv=True,
                    read_config=True,
                    rest_target='--fn'):
    options = {}
    for o in option_dicts:
        options = merge_options(options, o)

    if read_argv:
        options = merge_options(options, docopt(__doc__))

    if read_config:
        while True:
            configs = resolve(options['--config'],
                              default_modules=[cfg],
                              always_wrap=False)
            options['--config'] = []
            if not configs:
                break
            for config in configs:
                options = merge_options(config, options)

    return options


def main(*option_dicts, read_argv=True, read_config=True, rest_target='--fn'):
    options = resolve_options(*option_dicts,
                              read_argv=read_argv,
                              read_config=read_config,
                              rest_target=rest_target)
    options = process_options(options, rest_target)
    options['command'](Options(options))


if __name__ == '__main__':
    main()
