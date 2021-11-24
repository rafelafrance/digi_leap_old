// cppimport

#include "spell_well.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(spell_well_py, m) {
    m.doc() = "A simple spell checker.";

    py::class_<SpellWell>(m, "SpellWell")
        .def(py::init<std::unordered_map<std::u32string, long>&, std::u32string&,
                      long, long>(),
             py::arg("vocab"), py::arg("replacers") = defaultReplacers,
             py::arg("min_freq") = 5, py::arg("min_len") = 3);
        // .def("normalize", &SpellWell::normalize, py::arg("word"));
}

/*
  <%
  cfg['compiler_args'] = ['-std=c++17']
  cfg['sources'] = ['spell_well.cpp']
  setup_pybind11(cfg)
  %>
*/
