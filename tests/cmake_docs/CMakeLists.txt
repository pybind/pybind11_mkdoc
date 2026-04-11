cmake_minimum_required(VERSION 3.25...4.3)
project(sbox)

# Find Python
find_package(Python REQUIRED COMPONENTS Interpreter Development)

# Find pybind11
execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
find_package(pybind11 3.0 REQUIRED CONFIG)

# Find pybind11-mkdoc
execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import pybind11_mkdoc; print(pybind11_mkdoc.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_mkdoc_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
find_package(pybind11_mkdoc REQUIRED CONFIG)

# Add the pybind11 module
pybind11_add_module(my_pybind11_module dummy.cc)
target_include_directories(my_pybind11_module PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../sample_header_docs)
pybind11_mkdoc(
    OUTPUT my_module_docs.h 
    PYBIND11_MODULE my_pybind11_module
    EXTRA_ARGS $ENV{PYBIND11_TEST_EXTRA_ARGS}
    HEADERS 
        "../sample_header_docs/sample header with spaces.h"
        ${CMAKE_CURRENT_SOURCE_DIR}/../sample_header_docs/sample_header_2.h
)
