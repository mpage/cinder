import setuptools

from distutils.core import setup, Extension


_cinder = Extension(
    '_cinder',
    define_macros=[('MAJOR_VERSION', '0'),
                   ('MINOR_VERSION', '1')],
    include_dirs=['src'],
    sources=['src/cinder.c', 'src/ceval.c'])


setup(name='cinder',
      version='0.1',
      packages=setuptools.find_packages(exclude=['tests*']),
      ext_modules=[_cinder],
      setup_requires=["pytest-runner"],
      tests_require=["pytest"],
      python_requires='>=3.6')
