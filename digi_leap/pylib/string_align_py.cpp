// cppimport

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include "string_align.hpp"

namespace py = pybind11;

PYBIND11_MODULE(string_align_py, m) {
    m.doc() = "Align multiple strings.";
    m.def("align_all", &align_all, "Get the alignment string for a pair of strings.");
    m.def("levenshtein", &levenshtein, "Get the levenshtein distance for 2 strings.");
    m.def("levenshtein_all", &levenshtein_all,
        "Get the levenshtein distance for all pairs of strings in the list.");
}

/*
<%
cfg['compiler_args'] = ['-std=c++17']
cfg['sources'] = ['string_align.cpp']
setup_pybind11(cfg)
%>
*/
