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
])
def test_disassemble(function, expected_ir):
    cfg = bytecode.disassemble(function.__code__.co_code)
    print(str(cfg))
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
])
def test_reassemble(function):
    expected = function.__code__.co_code
    cfg = bytecode.disassemble(expected)
    actual = bytecode.assemble(cfg)
    assert actual == expected
