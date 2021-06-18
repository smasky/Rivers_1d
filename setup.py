'''
Author: smasky
Date: 2021-06-16 21:43:52
LastEditTime: 2021-06-16 23:23:06
LastEditors: smasky
Description: 
FilePath: \Rivers_1d\setup.py
You will never know unless you try
'''
from setuptools import setup,Extension
from Cython.Build import cythonize
import numpy
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
