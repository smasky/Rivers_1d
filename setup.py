from setuptools import setup, Extension
import pybind11

# 配置扩展模块
ext_modules = [
    Extension(
        'river1D',  # 模块的名称
        ['river1D.cpp', 'section.cpp' , 'reach.cpp'],  # C++ 源文件
        include_dirs=[
            pybind11.get_include(),  # 获取 pybind11 头文件
            pybind11.get_include(user=True)  # 获取用户安装的 pybind11 头文件
        ],
        language='c++',  # 使用 C++ 编译
    ),
]

# 调用 setuptools.setup 来创建模块
setup(
    name='river1D',
    version='0.1',
    ext_modules=ext_modules,
    install_requires=['pybind11'],  # 需要 pybind11 包
)
