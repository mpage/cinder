import ctypes

from cinder.util import get_private_symbol
from ctypes.util import find_library


_cinder_path = find_library('_cinder')
_cinder = ctypes.CDLL(_cinder_path)
_cinder.get_my_eval_breaker_address.restype = ctypes.c_void_p


def test_get_private_symbol():
    val = get_private_symbol(_cinder, '_my_eval_breaker', 'get_my_eval_breaker_address')
    assert val == _cinder.get_my_eval_breaker_address()
