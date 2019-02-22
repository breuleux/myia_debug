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
     [--interactive]
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
  -i --interactive      Show an interactive prompt afterwards.
"""

import operator
from docopt import docopt
from functools import reduce
from hrepr import hrepr

from myia.abstract import InferenceError
from myia.opt import lib as optlib
from myia.utils import merge
from myia.debug.traceback import print_inference_error

from . import cmd, cfg, typ, steps
from . import do_inject  # noqa: F401
from .tools import Options, Not
from .gprint import mcss
from buche import buche, reader, H, Repl


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

    refs = [r for r in refs if r]

    if len(refs) > 1:
        return do_all(refs, split=False)
    else:
        ref, = refs

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


code_globals = globals()


def run(command, options, interactive=None):
    if interactive is None:
        interactive = options['--interactive']

    if interactive:
        code_globals['options'] = options
        # buche.command_template(
        #     content=str(
        #         H.div['repl-box'](
        #             H.style(mcss),
        #             H.bucheLog(address="/"),
        #             H.bucheInput(address="/input")
        #         )
        #     )
        # )
        repl = Repl(
            buche,
            reader,
            code_globals=code_globals,
            address="/repl",
            log_address="/"
        )
        buche.command_template(content=str(hrepr(repl)))

    buche.master.send({
        "command": "redirect",
        "from": "/stdout",
        "to": "/"
    })

    try:
        res = command(Options(options))
        code_globals['res'] = res
    # except InferenceError as e:
    #     print_inference_error(e)
    except Exception as e:
        buche(e, interactive=True)

    # repl = buche['/']
    # inp = buche['/input']
    # saved = []
    # cmdlog = ['']
    # cmdidx = 0

    # @reader.on_keyup
    # def repl_key(event, message):
    #     nonlocal cmdidx
    #     key = message.which
    #     if key == 'Up':
    #         cmdidx = (cmdidx - 1) % len(cmdlog)
    #         inp.command_set(value=cmdlog[cmdidx])
    #     elif key == 'Down':
    #         cmdidx = (cmdidx + 1) % len(cmdlog)
    #         inp.command_set(value=cmdlog[cmdidx])

    # @reader.on_submit
    # def repl_line(event, message):
    #     nonlocal cmdidx
    #     code = message.value
    #     if code.strip() == '':
    #         return
    #     repl.html.logEntry['echo'](code)
    #     inp.command_set()
    #     try:
    #         try:
    #             res = eval(code, code_globals)
    #             if res is not None:
    #                 repl.show.logEntry['result'](res, interactive=True)
    #         except SyntaxError:
    #             exec(code, code_globals)
    #     except Exception as exc:
    #         repl.show.logEntry['error'](exc)
    #     cmdlog.append(code)
    #     cmdidx = 0

    # @reader.on_click
    # def repl_select(event, message):
    #     if hasattr(message, 'obj'):
    #         try:
    #             rank = saved.index(message.obj)
    #             varname = f'_{rank + 1}'
    #         except ValueError:
    #             saved.append(message.obj)
    #             rank = len(saved)
    #             varname = f'_{rank}'
    #             code_globals[varname] = message.obj
    #             repl.html.logEntry['echo'](f'{varname} = {message.obj}')
    #         inp.command_append(value=varname)
    #     inp.command_focus()

    # if interactive:
    #     inp.command_focus()
    #     reader.start()

    if interactive:
        repl.start(nodisplay=True)


def main(*option_dicts, read_argv=True, read_config=True, rest_target='--fn'):
    options = resolve_options(*option_dicts,
                              read_argv=read_argv,
                              read_config=read_config,
                              rest_target=rest_target)
    options = process_options(options, rest_target)
    run(options['command'], options)


if __name__ == '__main__':
    main()
