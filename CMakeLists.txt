cmake_minimum_required(VERSION 3.18)

project(digi_leap)
set(CMAKE_CXX_STANDARD 17)

add_subdirectory(extern/pybind11)

pybind11_add_module(levenshtein src/levenshtein.cpp)
