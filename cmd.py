
from . import steps

def show(o):
    res = o.run(default=[steps.parse,
                         steps.resolve,
                         steps.opt,
                         steps.export])
    g = res['graph']

    from myia.ir import ANFNode
    def ttip(node):
        if isinstance(node, ANFNode):
            return node.type

    buche(
        g,
        graph_width='95vw',
        graph_height='95vh',
        node_tooltip=ttip,
        # graph_beautify=False
    )
