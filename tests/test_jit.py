from cinder import jit


def test_jit():
    adder = jit.make_adder()
    result = adder()
    assert result == 100
