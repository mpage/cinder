#include <Python.h>

static PyModuleDef cinder_extension_module = {
  PyModuleDef_HEAD_INIT,
  .m_name = "_cinder",
  .m_doc  = "Cinder extension code",
  .m_size = -1,
};

PyMODINIT_FUNC
PyInit__cinder(void)
{
  PyObject* m = PyModule_Create(&cinder_extension_module);
  if (m == NULL) {
    return NULL;
  }

  printf("Hi matt\n");

  return m;
}
