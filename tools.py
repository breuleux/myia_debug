
from myia.api import parse as parse, \
    default_object_map, lax_type_map
from myia.prim.py_implementations import py_implementations
from myia.ir import GraphCloner
from myia.opt import (
    PatternEquilibriumOptimizer,
)


def process_function(fn, opts):
    g = parse(fn, resolve_globals=False)
    eq = PatternEquilibriumOptimizer(*opts)
    eq(g)
    return g


class Options:

    def __init__(self, options):
        self.options = options

    def get_function(self, apply_opts=True):
        fn, = self.options['fns']
        opts = self.options['opts'] if apply_opts else []
        return process_function(fn, opts)

    def __getitem__(self, key):
        return self.options[key]
