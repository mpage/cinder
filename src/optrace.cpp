#include <Python.h>
#include <frameobject.h>

#include "marshal.h"

extern "C" {

extern PyObject* EvalAndTraceFrame(PyFrameObject* f, int throwflag);
extern PyObject* ClearFrameTraces();

static _PyFrameEvalFunction old_tracer = nullptr;

static PyObject *
optrace_start_tracing(PyObject *self, PyObject* args) {
    PyThreadState *tstate = PyThreadState_GET();
    old_tracer = tstate->interp->eval_frame;
    tstate->interp->eval_frame = EvalAndTraceFrame;
    Py_RETURN_NONE;
}

static PyObject *
optrace_stop_tracing(PyObject *self, PyObject* args) {
    PyThreadState *tstate = PyThreadState_GET();
    tstate->interp->eval_frame = old_tracer;
    return ClearFrameTraces();
}

static void
optrace_free(void* module) {
    // Clear any lingering frame traces before the interpreter is
    // destroyed. This ensures that any references to python objects that are
    // retained by the frame traces are destroyed while the interpreter is
    // still alive.
    ClearFrameTraces();
}

static PyMethodDef OptraceMethods[] = {
    {"start_tracing",  optrace_start_tracing, METH_NOARGS,
     "Start tracing opcodes."},
    {"stop_tracing", optrace_stop_tracing, METH_NOARGS,
     "Stop tracing opcodes."},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef optracemodule = {
    PyModuleDef_HEAD_INIT,
    "optrace",
    NULL,
    -1,
    OptraceMethods,
    nullptr,        // m_slots
    nullptr,        // m_traverse
    nullptr,        // m_clear
    optrace_free   // m_free
};

PyMODINIT_FUNC PyInit_optrace(void) {
    PyObject* module = PyModule_Create(&optracemodule);
    optrace::InitPyTypes(module);
    return module;
}

}  // extern "C"
