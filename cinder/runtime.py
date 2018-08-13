import ctypes

from cinder.util import get_private_symbol
from ctypes.util import find_library

_cinder_name = find_library('_cinder')
_cinder = ctypes.CDLL(_cinder_name)  # type: ignore
_cinder.get_call_function_address.restype = ctypes.c_void_p
_cinder.initialize_scheduler.argtypes = [ctypes.c_void_p, ctypes.c_void_p]


def patch_scheduler() -> None:
    eval_breaker = get_private_symbol(ctypes.pythonapi, '_eval_breaker.0', 'PyObject_GenericGetAttr')
    print(f'Evalb={hex(eval_breaker)}')
    pendingcalls = get_private_symbol(ctypes.pythonapi, '_pendingcalls_to_do.0', 'PyObject_GenericGetAttr')
    print(f'Pending={hex(pendingcalls)}')
    _cinder.initialize_scheduler(eval_breaker, pendingcalls)
