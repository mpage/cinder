import pytest

from cinder import bytecode


def single_block():
    return 123


def cond_jump(x):
    if x:
        return 1
    return 2


def nested_cond_jump(x, y):
    if x:
        if y:
            return 1
        return 2
    elif y:
        return 3
    return 4


def load_attr(x):
    return x.foo


def unary_not(x):
    return not x


def two_way_cond(x, y, z):
    return x or (not y and z)


def store_local(x):
    y = x
    return y


def while_loop(x):
    while x:
        pass
    return x


def store_attr(x, v):
    x.foo = v
    return x


def load_global():
    return bar


def do_call(f):
    return f(1)


def jump_forward(x, y, z):
    if x:
        if y:
            z = 1
    else:
        z = 2


def cmp_is(x, y):
    return x is y


def cmp_is_not(x, y):
    return x is not y


def loop_with_setup(x, y):
    x = y
    while x:
        pass
    return x


@pytest.mark.parametrize("function,expected_ir", [
    (single_block, """entry:
bb0:
  LOAD 1 CONSTANTS
  RETURN_VALUE"""),

    (cond_jump, """entry:
bb0:
  LOAD 0 LOCALS
  COND_BRANCH true=bb1 false=bb2
bb1:
  LOAD 1 CONSTANTS
  RETURN_VALUE
bb2:
  LOAD 2 CONSTANTS
  RETURN_VALUE"""),

    (nested_cond_jump, """entry:
bb0:
  LOAD 0 LOCALS
  COND_BRANCH true=bb1 false=bb4
bb1:
  LOAD 1 LOCALS
  COND_BRANCH true=bb2 false=bb3
bb2:
  LOAD 1 CONSTANTS
  RETURN_VALUE
bb3:
  LOAD 2 CONSTANTS
  RETURN_VALUE
bb4:
  LOAD 1 LOCALS
  COND_BRANCH true=bb5 false=bb6
bb5:
  LOAD 3 CONSTANTS
  RETURN_VALUE
bb6:
  LOAD 4 CONSTANTS
  RETURN_VALUE"""),

    (load_attr, """entry:
bb0:
  LOAD 0 LOCALS
  LOAD_ATTR 0
  RETURN_VALUE"""),

    (unary_not, """entry:
bb0:
  LOAD 0 LOCALS
  UNARY_OP NOT
  RETURN_VALUE"""),

    (two_way_cond, """entry:
bb0:
  LOAD 0 LOCALS
  COND_BRANCH true=bb3 false=bb1
bb1:
  LOAD 1 LOCALS
  UNARY_OP NOT
  COND_BRANCH true=bb2 false=bb3
bb2:
  LOAD 2 LOCALS
bb3:
  RETURN_VALUE"""),

    (store_local, """entry:
bb0:
  LOAD 0 LOCALS
  STORE 1
  LOAD 1 LOCALS
  RETURN_VALUE"""),

    (while_loop, """entry:
bb1:
  LOAD 0 LOCALS
  COND_BRANCH true=bb2 false=bb3
bb2:
  BRANCH bb1
bb3:
  LOAD 0 LOCALS
  RETURN_VALUE"""),

    (store_attr, """entry:
bb0:
  LOAD 1 LOCALS
  LOAD 0 LOCALS
  STORE_ATTR 0
  LOAD 0 LOCALS
  RETURN_VALUE"""),

    (load_global, """entry:
bb0:
  LOAD_GLOBAL 0
  RETURN_VALUE"""),

    (do_call, """entry:
bb0:
  LOAD 0 LOCALS
  LOAD 1 CONSTANTS
  CALL 1
  RETURN_VALUE"""),

    (jump_forward, """entry:
bb0:
  LOAD 0 LOCALS
  COND_BRANCH true=bb1 false=bb3
bb1:
  LOAD 1 LOCALS
  COND_BRANCH true=bb2 false=bb4
bb2:
  LOAD 1 CONSTANTS
  STORE 2
  BRANCH bb4
bb3:
  LOAD 2 CONSTANTS
  STORE 2
bb4:
  LOAD 0 CONSTANTS
  RETURN_VALUE"""),

    (cmp_is, """entry:
bb0:
  LOAD 0 LOCALS
  LOAD 1 LOCALS
  COMPARE IS
  RETURN_VALUE"""),

    (cmp_is_not, """entry:
bb0:
  LOAD 0 LOCALS
  LOAD 1 LOCALS
  COMPARE IS_NOT
  RETURN_VALUE"""),

    (loop_with_setup, """entry:
bb0:
  LOAD 1 LOCALS
  STORE 0
bb1:
  LOAD 0 LOCALS
  COND_BRANCH true=bb2 false=bb3
bb2:
  BRANCH bb1
bb3:
  LOAD 0 LOCALS
  RETURN_VALUE"""),
])
def test_disassemble(function, expected_ir):
    cfg = bytecode.disassemble(function.__code__.co_code)
    assert str(cfg) == expected_ir


@pytest.mark.parametrize("function", [
    single_block,
    cond_jump,
    nested_cond_jump,
    load_attr,
    unary_not,
    two_way_cond,
    store_local,
    while_loop,
    store_attr,
    load_global,
    do_call,
    jump_forward,
    cmp_is,
    cmp_is_not,
    loop_with_setup,
])
def test_reassemble(function):
    expected = function.__code__.co_code
    cfg = bytecode.disassemble(expected)
    actual = bytecode.assemble(cfg)
    assert actual == expected
