// cppimport

#include "line_align.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(line_align_py, m) {
    m.doc() = "Align multiple strings.";

    m.attr("gap_char") = gap_char;

    m.def("align_all", &align_all, "Get the alignment string for a pair of strings.",
          py::arg("strings"), py::arg("substitutions"), py::arg("gap") = -3.0,
          py::arg("skew") = -0.5);

    m.def("levenshtein", &levenshtein, "Get the levenshtein distance for 2 strings.");

    m.def("levenshtein_all", &levenshtein_all,
          "Get the levenshtein distance for all pairs of strings in the list.");
}

/*
  <%
  cfg['compiler_args'] = ['-std=c++17']
  cfg['sources'] = ['line_align.cpp']
  setup_pybind11(cfg)
  %>
*/
