// cppimport

#include <algorithm>
#include <cstddef>
#include <iostream>
#include <numeric>
#include <string>
#include <tuple>
#include <utility>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
//#include "helpers.cpp"

namespace py = pybind11;

size_t distance(std::u32string& str1, std::u32string& str2) {
    const size_t len1 = str1.length();
    const size_t len2 = str2.length();

    if (len1 == 0) { return len2; }
    if (len2 == 0) { return len1; }

    std::vector<size_t> dist(len2 + 1);
    std::iota(dist.begin(), dist.end(), 0);

    for (size_t i = 0; i < len1; ++i) {
        size_t prev_dist = i;
        for (size_t j = 0; j < len2; ++j) {
            dist[j + 1] = std::min({
                std::exchange(prev_dist, dist[j + 1]) + (str1[i] == str2[j] ? 0 : 1),
                dist[j] + 1,
                dist[j + 1] + 1
            });
        }
    }
    return dist[len2];
}

//std::string align(std::u32string& str1, std::u32string& str2) {
//    std::vector<std::string> temp = {"one ", "two ", "three"};
//    return concat(begin(temp), end(temp));
//}

std::vector<std::tuple<size_t, size_t, size_t>>
distance_all(std::vector<std::u32string> lines) {
    const size_t len = lines.size();

    std::vector<std::tuple<size_t, size_t, size_t>> results;

    for (size_t i = 0; i < len - 1; ++i) {
        for (size_t j = i + 1; j < len; ++j) {
            auto dist = distance(lines[i], lines[j]);
            results.push_back(std::make_tuple(i, j, dist));
        }
    }

    std::stable_sort(begin(results), end(results),
        [](auto const &t1, auto const &t2) {
            return std::get<2>(t1) < std::get<2>(t2);
        });

    return results;
}


PYBIND11_MODULE(levenshtein, m) {
  m.doc() = "Levenshtein distance for multiple sequences.";
//  m.def("align", &align, "Get the alignment string for a pair of strings.");
  m.def("distance", &distance, "Get the levenshtein distance for 2 strings.");
  m.def("distance_all", &distance_all,
    "Get the levenshtein distance for all pairs of strings in the list.");
}

/*
<%
cfg['compiler_args'] = ['-std=c++17']
setup_pybind11(cfg)
%>
*/
