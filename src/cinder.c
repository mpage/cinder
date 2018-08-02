#include <Python.h>

static PyModuleDef cinder_extension_module = {
  PyModuleDef_HEAD_INIT,
  .m_name = "_cinder",
  .m_doc  = "Cinder extension code",
  .m_size = -1,
};

// Bottom-most entry point to a JitFunction
typedef PyObject* (*jit_function_entry_t)(PyObject**);

typedef struct {
  PyObject_HEAD
  jit_function_entry_t entry;
} JitFunction;

static int
JitFunction_init(PyObject* self, PyObject* args, PyObject* kwargs) {
  (void) kwargs;

  unsigned long address;
  if (!PyArg_ParseTuple(args, "k", &address)) {
    return -1;
  }

  ((JitFunction*) self)->entry = (jit_function_entry_t) address;

  return 0;
}

static PyTypeObject JitFunctionType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  .tp_name = "cinder.JitFunction",
  .tp_doc = "Jit compiled python functions",
  .tp_basicsize = sizeof(JitFunctionType),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = PyType_GenericNew,
  .tp_init = (initproc) JitFunction_init,
};

PyMODINIT_FUNC
PyInit__cinder(void)
{
  if (PyType_Ready(&JitFunctionType) < 0) {
    return NULL;
  }

  PyObject* m = PyModule_Create(&cinder_extension_module);
  if (m == NULL) {
    return NULL;
  }

  printf("Hi matt\n");

  Py_INCREF(&JitFunctionType);
  PyModule_AddObject(m, "JitFunction", (PyObject *) &JitFunctionType);

  return m;
}
