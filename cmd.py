
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


def grad(o):
    from myia.grad import grad

    g = o.run(default=[steps.parse, steps.resolve])['graph']
    gg = grad(g)
    buche(gg,
          graph_width='95vw',
          graph_height='95vh')


def grad2(o):
    from collections import defaultdict
    from myia.grad import grad2
    from myia.pipeline import PipelineStep
    from myia.ir import Graph

    nums = {}

    class GradStep(PipelineStep):
        def step(self, graph):
            return {'graph': grad2(graph)}

    grad_step = GradStep.partial()
    grad_step._name = 'grad'

    history = defaultdict(dict)

    def log(_, frame, node, value):
        if frame not in nums:
            nums[frame] = str(len(nums))
        history[node][nums[frame]] = value

    def ttip(node):
        if not isinstance(node, Graph):
            return history[node]

    def ttip2(node):
        if not isinstance(node, Graph):
            if node.graph:
                return node in node.graph.nodes

    res = o.run(default=[steps.parse,
                         steps.resolve,
                         grad_step,
                         steps.opt,
                         steps.export],
                config={'export.callback': log})

    g = res['graph']

    try:
        out = res['output']
        val, bprop = out(4)
        buche(val)
        buche(bprop(1))
    except Exception as e:
        buche(e)

    buche(g,
          graph_width='95vw',
          graph_height='95vh',
          node_tooltip=ttip,
        #   graph_beautify=False
          )

    # g = o.run(default=[steps.parse, steps.resolve, steps.opt])['graph']
    # gg = grad2(g)

    # buche(gg,
    #     #   graph_beautify=False,
    #       graph_width='95vw',
    #       graph_height='95vh')
