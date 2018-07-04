
from myia.opt import lib
from myia.prim import ops as P


tuple_opts = [
    lib.getitem_tuple,
    lib.setitem_tuple,
    lib.head_tuple,
    lib.tail_tuple,
    lib.bubble_op_cons,
    lib.bubble_op_nil,
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


all_opt = [
    *tuple_opts,
    *arith_opts,
    lib.inline,
]


grad_kit = [
    *tuple_opts,
    *arith_opts,
    lib.expand_J,
    lib.expand_Jinv,
    lib.inline,
    lib.J_Jinv_cancel,
    lib.Jinv_J_cancel,
    lib.drop_into_call,
    lib.drop_into_if,
    # lib.drop_getitem_into_if,
]
