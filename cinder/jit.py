from peachpy import *
from peachpy.x86_64 import *

from ctypes import pythonapi


def make_adder():
    with Function("test_add", (), int64_t) as func:
        MOV(rax, 100)
        RETURN(rax)
    encoded_function = func.finalize(abi.detect()).encode()
    return encoded_function.load()
