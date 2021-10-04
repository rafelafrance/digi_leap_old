#include <pybind11/pybind11.h>
#include <string>

namespace py = pybind11;

int score(int i, int j) { return i + j; }

PYBIND11_MODULE(levenshtein, m) {
  m.doc() = "Levenshtein distance for multiple sequences.";
  m.def("score", &score, "Get the levenshtein score for 2 strings.");
}
