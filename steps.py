
from myia.utils import Partial
from myia.pipeline.steps import (
    step_parse as parse,
    step_resolve as resolve,
    step_infer as infer,
    step_specialize as specialize,
    step_erase_class as erase_class,
    step_opt as opt,
    step_erase_tuple as erase_tuple,
    step_validate as validate,
    step_cconv as cconv,
)
from myia.compile import step_export as export

standard = [
    parse, resolve, infer, specialize,
    erase_class, opt, erase_tuple,
    validate, cconv, export
]

_bang_parse = standard[:standard.index(parse) + 1]
_bang_resolve = standard[:standard.index(resolve) + 1]
_bang_infer = standard[:standard.index(infer) + 1]
_bang_specialize = standard[:standard.index(specialize) + 1]
_bang_erase_class = standard[:standard.index(erase_class) + 1]
_bang_opt = standard[:standard.index(opt) + 1]
_bang_erase_tuple = standard[:standard.index(erase_tuple) + 1]
_bang_validate = standard[:standard.index(validate) + 1]
_bang_cconv = standard[:standard.index(cconv) + 1]
_bang_export = standard[:standard.index(export) + 1]


def _adjust():
    for name, g in globals().items():
        if isinstance(g, Partial):
            g._name = name


_adjust()
