cmake_minimum_required(VERSION 3.25)
project(pybind11_mkdoc)

include(CMakePackageConfigHelpers)

# Generate version file
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/pybind11_mkdocConfigVersion.cmake"
    VERSION 2.6.2
    COMPATIBILITY SameMajorVersion
)

# Create config file
configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/pybind11_mkdocConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/pybind11_mkdocConfig.cmake"
    INSTALL_DESTINATION pybind11_mkdoc
)

# Install config + version
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/pybind11_mkdocConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/pybind11_mkdocConfigVersion.cmake"
    DESTINATION pybind11_mkdoc
)

# Install functions
install(FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/pybind11_mkdoc_functions.cmake"
    DESTINATION pybind11_mkdoc
)
