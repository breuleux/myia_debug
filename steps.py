
from myia.pipeline import Partial
from myia.api import (
    step_parse as parse,
    step_resolve as resolve,
    step_infer as infer,
    step_specialize as specialize,
    step_prepare as prepare,
    step_opt as opt,
    step_validate as validate,
    step_cconv as cconv,
    step_export as export,
)

standard = [
    parse, resolve, infer, specialize, prepare, opt, validate, cconv, export
]

_bang_parse = standard[:standard.index(parse) + 1]
_bang_resolve = standard[:standard.index(resolve) + 1]
_bang_infer = standard[:standard.index(infer) + 1]
_bang_specialize = standard[:standard.index(specialize) + 1]
_bang_prepare = standard[:standard.index(prepare) + 1]
_bang_opt = standard[:standard.index(opt) + 1]
_bang_validate = standard[:standard.index(validate) + 1]
_bang_cconv = standard[:standard.index(cconv) + 1]
_bang_export = standard[:standard.index(export) + 1]


def _adjust():
    for name, g in globals().items():
        if isinstance(g, Partial):
            g._name = name


_adjust()
