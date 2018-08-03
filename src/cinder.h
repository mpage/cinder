#pragma once

#include <Python.h>

// Bottom-most entry point to a JitFunction
typedef PyObject* (*jit_function_entry_t)(PyObject**);

typedef struct {
  PyObject_HEAD
  jit_function_entry_t entry;
  PyObject* code_handle;
} JitFunction;
