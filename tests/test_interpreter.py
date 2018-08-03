import cinder

def identity(x):
    return x


def test_interpreter():
    cinder.install_interpreter()
    assert identity(1) == 1
    cinder.uninstall_interpreter()
