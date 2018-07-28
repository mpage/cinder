import dis
import pytest

from cinder import bytecode


def single_block():
    return 123


def cond_jump(x):
    if x:
        return 1
    return 2


@pytest.mark.parametrize("function,expected_ir", [
    (single_block, """entry:
bb0:
  LOAD_CONST 1
  RETURN_VALUE"""),

    (cond_jump, """entry:
bb0:
  LOAD_FAST 0
  COND_BRANCH true=bb1 false=bb2
bb1:
  LOAD_CONST 1
  RETURN_VALUE
bb2:
  LOAD_CONST 2
  RETURN_VALUE"""),
])
def test_disassemble(function, expected_ir):
    cfg = bytecode.disassemble(function.__code__.co_code)
    assert str(cfg) == expected_ir


@pytest.mark.parametrize("function", [
    single_block,
    cond_jump,
])
def test_reassemble(function):
    expected = function.__code__.co_code
    cfg = bytecode.disassemble(expected)
    actual = bytecode.assemble(cfg)
    assert actual == expected
