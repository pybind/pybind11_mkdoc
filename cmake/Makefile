.PHONY: all

all : ../pybind11_mkdoc/share/cmake/pybind11_mkdoc

build: CMakeLists.txt
	cmake -B build -S . -DCMAKE_INSTALL_PREFIX=../pybind11_mkdoc/share/cmake

../pybind11_mkdoc/share/cmake/pybind11_mkdoc: pybind11_mkdocConfig.cmake.in pybind11_mkdoc_functions.cmake build
	cmake --build build
	cmake --install build
