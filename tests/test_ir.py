import dis
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


@pytest.mark.parametrize("function,expected_ir", [
    (single_block, """entry:
bb0:
  LOAD_REF 1 CONSTANTS
  RETURN_VALUE"""),

    (cond_jump, """entry:
bb0:
  LOAD_REF 0 LOCALS
  COND_BRANCH true=bb1 false=bb2
bb1:
  LOAD_REF 1 CONSTANTS
  RETURN_VALUE
bb2:
  LOAD_REF 2 CONSTANTS
  RETURN_VALUE"""),

    (nested_cond_jump, """entry:
bb0:
  LOAD_REF 0 LOCALS
  COND_BRANCH true=bb1 false=bb4
bb1:
  LOAD_REF 1 LOCALS
  COND_BRANCH true=bb2 false=bb3
bb2:
  LOAD_REF 1 CONSTANTS
  RETURN_VALUE
bb3:
  LOAD_REF 2 CONSTANTS
  RETURN_VALUE
bb4:
  LOAD_REF 1 LOCALS
  COND_BRANCH true=bb5 false=bb6
bb5:
  LOAD_REF 3 CONSTANTS
  RETURN_VALUE
bb6:
  LOAD_REF 4 CONSTANTS
  RETURN_VALUE"""),

    (load_attr, """entry:
bb0:
  LOAD_REF 0 LOCALS
  LOAD_ATTR 0
  RETURN_VALUE"""),

    (unary_not, """entry:
bb0:
  LOAD_REF 0 LOCALS
  UNARY_OP NOT
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
])
def test_reassemble(function):
    expected = function.__code__.co_code
    cfg = bytecode.disassemble(expected)
    actual = bytecode.assemble(cfg)
    assert actual == expected
