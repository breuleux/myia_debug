
from myia.api import lax_converter
from myia.opt import lib
from myia.vm import VM
from myia.prim import ops as P
from myia.prim.py_implementations import \
    vm_implementations as vmimpl, \
    py_implementations as pyimpl


tuple_opts = [
    lib.getitem_tuple,
    lib.setitem_tuple,
    lib.head_tuple,
    lib.tail_tuple,
    # lib.bubble_op_cons,
    # lib.bubble_op_nil,
    lib.bubble_op_cons_binary,
    lib.bubble_op_nil_binary,
]


arith_opts = [
    lib.multiply_by_zero_l,
    lib.multiply_by_zero_r,
    lib.multiply_by_one_l,
    lib.multiply_by_one_r,
    lib.add_zero_l,
    lib.add_zero_r,
]


# _pyimpl = dict(pyimpl)
# del _pyimpl[P.cons_tuple]
# constant_prop = lib.make_constant_prop(vmimpl, _pyimpl, VM)


resolve_globals = lib.make_resolver(lax_converter())


all_opt = [
    *tuple_opts,
    *arith_opts,
    lib.inline,
    # lib.constant_prop,
    # lib.J_Jinv_cancel,
    # lib.Jinv_J_cancel,
    # lib.drop_into_call,
    # lib.drop_into_if,
    # lib.drop_getitem_into_if,
]
