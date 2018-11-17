
from myia.ir import ANFNode

from . import steps
from buche import buche


def show(o):
    res = o.run(default=[steps.parse,
                         steps.resolve])
    if 'error' in res:
        raise res['error']

    g = res['graph']

    def ttip(node):
        if isinstance(node, ANFNode):
            return node.inferred

    buche(
        g,
        graph_width='95vw',
        graph_height='95vh',
        node_tooltip=ttip,
        function_in_node=not o['--function-nodes'],
        graph_beautify=not o['--no-beautify'] and not o['--function-nodes'],
    )


def run(o):
    res = o.run(default=[steps.parse,
                         steps.resolve,
                         steps.infer,
                         steps.specialize,
                         steps.opt,
                         steps.debug_export])
    if 'error' in res:
        raise res['error']

    f = res['output']

    print('Result:', f(*o['args']))
