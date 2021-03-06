#include <Python.h>
#include <frameobject.h>

#include "cinder.h"

static int
JitFunction_init(JitFunction* self, PyObject* args, PyObject* kwargs) {
  (void) kwargs;

  unsigned long address;
  PyObject* code_handle;
  if (!PyArg_ParseTuple(args, "Ok", &code_handle, &address)) {
    return -1;
  }

  self->entry = (jit_function_entry_t) address;
  Py_INCREF(code_handle);
  self->code_handle = code_handle;

  return 0;
}

static void
JitFunction_dealloc(JitFunction* self)
{
    Py_DECREF(self->code_handle);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject*
JitFunction_call(JitFunction* self, PyObject* args, PyObject* kwargs) {
  // TODO(mpage): Make this real - keywords and defaulting
  Py_ssize_t num_items = PyTuple_Size(args);
  PyObject** items = (PyObject**) alloca(num_items * sizeof(PyObject*));
  assert(items != NULL);
  for (int i = 0; i < num_items; i++) {
    items[i] = PyTuple_GetItem(args, i);
  }
  return self->entry(items);
}

PyTypeObject JitFunctionType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  .tp_name = "cinder.JitFunction",
  .tp_doc = "Jit compiled python functions",
  .tp_basicsize = sizeof(JitFunctionType),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT,
  .tp_new = PyType_GenericNew,
  .tp_init = (initproc) JitFunction_init,
  .tp_dealloc = (destructor) JitFunction_dealloc,
  .tp_call = (ternaryfunc) JitFunction_call,
};

static _PyFrameEvalFunction old_eval_frame = NULL;

extern PyObject* cinder_eval_frame(PyFrameObject* f, int throwflag);

static PyObject *
cinder_install_interpreter(PyObject *self, PyObject* args) {
  PyThreadState *tstate = PyThreadState_GET();
  old_eval_frame = tstate->interp->eval_frame;
  tstate->interp->eval_frame = cinder_eval_frame;
  Py_RETURN_NONE;
}

static PyObject *
cinder_uninstall_interpreter(PyObject *self, PyObject* args) {
  PyThreadState *tstate = PyThreadState_GET();
  // TODO(mpage): Check that old_eval_frame is not null. Raise an
  // exception if so.
  tstate->interp->eval_frame = old_eval_frame;
  Py_RETURN_NONE;
}

static PyMethodDef cinder_methods[] = {
  {"install_interpreter",  cinder_install_interpreter, METH_NOARGS,
   "Install the cinder interpreter loop."},
  {"uninstall_interpreter", cinder_uninstall_interpreter, METH_NOARGS,
   "Uninstall the cinder interpreter loop."},
  {NULL, NULL, 0, NULL}
};

static PyModuleDef cinder_extension_module = {
  PyModuleDef_HEAD_INIT,
  .m_name = "_cinder",
  .m_doc  = "Cinder extension code",
  .m_methods = cinder_methods,
  .m_size = -1,
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

  Py_INCREF(&JitFunctionType);
  PyModule_AddObject(m, "JitFunction", (PyObject *) &JitFunctionType);

  return m;
}
