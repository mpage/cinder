import ctypes
import lief  # type: ignore


from typing import Optional


class DlInfo(ctypes.Structure):
    _fields_ = [
        ('dli_fname', ctypes.c_char_p),
        ('dli_fbase', ctypes.c_void_p),
        ('dli_sname', ctypes.c_char_p),
        ('dli_saddr', ctypes.c_void_p),
    ]


DlInfoPointer = ctypes.POINTER(DlInfo)


libdl = ctypes.CDLL(None)  # type: ignore  -- Incorrect typeshed stub
libdl.dlsym.restype = ctypes.c_void_p

libdl.dladdr.argtypes = [ctypes.c_void_p, DlInfoPointer]
libdl.dladdr.restype = ctypes.c_int


class SymbolResolutionError(Exception):
    pass


def get_private_symbol(lib: ctypes.CDLL, symbol_name: str, known_symbol_name: str) -> int:
    """Look up a symbol with internal linkage"""
    # Get filename + base address of shared library that contains the symbol we care about
    known_sym = libdl.dlsym(lib._handle, known_symbol_name.encode())
    if known_sym is None:
        raise SymbolResolutionError(f"dlsym() failed for {known_symbol_name}")
    info = DlInfo()
    if libdl.dladdr(known_sym, ctypes.byref(info)) == 0:
        raise SymbolResolutionError(f"dladdr() failed for {known_symbol_name}")
    # Parse the symbol table
    binary = lief.parse(info.dli_fname)
    symbol = binary.get_symbol(symbol_name)
    # LIEF tries to be too helpful and relocates the virtual address of each symbol for us.
    # In the face of ASLR that may be incorrect. So we reverse engineer the raw symbol table
    # value.
    start_addr = -1
    for segment in binary.segments:
        if segment.file_offset == 0:
            start_addr = segment.virtual_address
            break
    if start_addr == -1:
        raise SymbolResolutionError('Cannot compute base address from shared library')
    raw_value = symbol.value - start_addr
    return info.dli_fbase + raw_value
