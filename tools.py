
from myia.api import parse as parse, standard_pipeline
from myia.prim.py_implementations import py_implementations
from myia.ir import GraphCloner
from myia.opt import (
    PatternEquilibriumOptimizer,
)
from myia.pipeline import PipelineDefinition, Merge

from . import steps


class Not:
    def __init__(self, value):
        self.value = value


class Options:

    def __init__(self, options):
        self.options = options

    def pipeline(self, default=steps.standard, config=None):
        all_steps = self.options['pipeline']
        pos = [p for p in all_steps if not isinstance(p, Not)]
        neg = {p.value for p in all_steps if isinstance(p, Not)}
        if not pos:
            pos = default
        final = [p for p in pos if p not in neg]
        pdef = PipelineDefinition(
            resources=standard_pipeline.resources,
            steps={p._name: p for p in final}
        )
        opts = self.options['opts']
        if opts and steps.opt not in final:
            raise Exception('Optimizations can only be applied if the'
                            ' opt step is in the pipeline')
        elif opts:
            pdef = pdef.configure({'opt.opts': Merge(opts)})

        if config:
            pdef = pdef.configure(config)

        return pdef.make()

    def run(self, default=steps.standard, config=None):
        fn, = self.options['fns']
        pip = self.pipeline(default=default, config=config)
        argspec = self.argspec()
        return pip(input=fn, argspec=argspec)

    def argspec(self):
        ovalues = self['args']
        otypes = self['types']

        args = [{} for _ in range(max(len(ovalues), len(otypes)))]
        for a, value in zip(args, ovalues):
            a['value'] = value if value is not None else ANYTHING
        for a, typ in zip(args, otypes):
            a['type'] = typ

        return args

    def __getitem__(self, key):
        return self.options[key]
