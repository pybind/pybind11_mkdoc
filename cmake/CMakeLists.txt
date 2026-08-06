cmake_minimum_required(VERSION 3.25...4.3)

# Read the version from the Python package; project() accepts numeric components only,
# so any dev/pre-release suffix is dropped.
file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/../pybind11_mkdoc/__init__.py" version_line
    REGEX "^__version__ *= *[\"']"
)
if(NOT version_line MATCHES "([0-9]+(\\.[0-9]+)*)")
    message(FATAL_ERROR "Could not read __version__ from pybind11_mkdoc/__init__.py")
endif()

project(pybind11_mkdoc VERSION "${CMAKE_MATCH_1}")

include(CMakePackageConfigHelpers)

# Generate version file
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/pybind11_mkdocConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
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
