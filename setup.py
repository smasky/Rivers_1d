from setuptools import setup,Extension
from Cython.Build import cythonize
import numpy
import scipy
setup(ext_modules = cythonize(Extension(
'rivers_1d',
sources=['rivers_1d.pyx','utils.cpp','control.cpp','reaches.cpp'],
language='c++',
include_dirs=[numpy.get_include()],
library_dirs=[],
libraries=[],
extra_compile_args=[],
extra_link_args=[]
)))
