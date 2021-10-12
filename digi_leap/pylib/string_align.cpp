// cppimport

/*
    Naive implementations based on Gusfield 1997
    I.e. There's plenty of room for improvement.

    This code is for a singular use, to perform a multiple sequence alignment on
    similar short text fragments. That is if I am given a set of text lines like:

        MOJAVE DESERT, PROVIDENCE MTS.: canyon above
        E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above
        Be ‘MOJAVE DESERT, PROVIDENCE canyon “above
        E MOJAVE DESERT PROVTDENCE MTS. # canyon above

    I should get back something similar to:

        ⋄⋄⋄⋄MOJAVE DESERT⋄, PROVIDENCE MTS⋄.⋄: canyon ⋄above
        ⋄E. MOJAVE DESERT , PROVIDENCE MTS . : canyon ⋄above
        Be ‘MOJAVE DESERT⋄, PROVIDENCE ⋄⋄⋄⋄⋄⋄⋄⋄canyon “above
        ⋄E⋄ MOJAVE DESERT⋄⋄ PROVTDENCE MTS⋄. # canyon ⋄above

    Where "⋄" characters are used to represent gaps in the alignments.

    The ultimate goal is to use this alignment to build a consensus sequence.

    To do this I am using a modified Needleman-Wunsch global alignment algorithm.
    Some of the changes are:

        - The similarity matrix is based upon visual similarity and, obviously,
          not on anything biological.
        - I build the multiple alignment up from the strings in order where most
          multiple alignment algorithms use phylogeny to guide the process.
          Note that, elsewhere, I use the Levenshtein distance to create a
          pseudo-phylogeny to order the strings.
        - I actually align one sequence to many vs. pairwise build ups.
        - The trace back matrix is built in reverse so I don't have to reverse
          the strings. Maybe I should move to buffered c-strings instead.
*/


#include <algorithm>
#include <codecvt>
#include <cstddef>
#include <exception>
#include <iostream>
#include <iterator>
#include <limits>
#include <locale>
#include <numeric>
#include <sstream>
#include <tuple>
#include <utility>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

std::unordered_map<std::u32string, float> weight = {
    {U"aa", 1.0},
    {U"ab", 0.475},
    {U"ba", 0.475},
};

const char32_t gap_char = U'⋄';

template<typename Iter> std::string concat(Iter first, Iter last)
{
    if (first == last) { return ""; }

    std::stringstream ss;

    while (first != last) {
        ss << *first;
        ++first;
    }

    return ss.str();
}


std::string convert(const std::u32string wide) {
    std::wstring_convert<std::codecvt_utf8<char32_t>,char32_t> conv;
    return conv.to_bytes(wide);
}


long levenshtein(std::u32string& str1, std::u32string& str2) {
    const long len1 = str1.length();
    const long len2 = str2.length();

    if (len1 == 0) { return len2; }
    if (len2 == 0) { return len1; }

    std::vector<long> dist(len2 + 1);
    std::iota(dist.begin(), dist.end(), 0);

    for (long r = 0; r < len1; ++r) {
        long prev_dist = r;
        for (long c = 0; c < len2; ++c) {
            dist[c + 1] = std::min({
                std::exchange(prev_dist, dist[c + 1]) + (str1[r] == str2[c] ? 0 : 1),
                dist[c] + 1,
                dist[c + 1] + 1
            });
        }
    }
    return dist[len2];
}

std::vector<std::tuple<long, long, long>>
levenshtein_all(std::vector<std::u32string> lines) {
    const long len = lines.size();

    std::vector<std::tuple<long, long, long>> results;

    for (long i = 0; i < len - 1; ++i) {
        for (long j = i + 1; j < len; ++j) {
            auto dist = levenshtein(lines[i], lines[j]);
            results.push_back(std::make_tuple(dist, i, j));
        }
    }

    std::stable_sort(begin(results), end(results),
        [](auto const &t1, auto const &t2) {
            return std::get<0>(t1) < std::get<0>(t2);
        });

    return results;
}

typedef std::tuple<long, std::u32string, std::u32string, long> Alignment;
typedef std::vector<Alignment> Alignments;

struct Traceback {
    float V;
    float G;
    float E;
    float F;
    Traceback(): V(0.0), G(0.0), E(0.0), F(0.0) {}
};
typedef std::vector<std::vector<Traceback>> TraceMatrix;

std::vector<std::u32string> align(
        std::vector<std::u32string> strings,
        float gap_open = 5.0,
        float gap_extend = 1.0
) {
    if (strings.size() < 1) {
        throw std::invalid_argument("You must enter at least one string.");
    }

    Alignments aligns;
    std::vector<std::u32string> results;

    results.push_back(strings[0]);

    for (size_t s = 1; s < strings.size(); ++s) {

        // Build the matrix

        TraceMatrix trace(
            results[0].length()+1,
            std::vector<Traceback>(strings[s].length()+1));

        float g = -gap_open;
        for (size_t i = 1; i <= results[0].length(); ++i) {
            trace[i][0].V = g;
            trace[i][0].E = g;
            g -= gap_extend;
        }

        g = -gap_open;
        for (size_t j = 1; j <= strings[s].length(); ++j) {
            trace[0][j].V = g;
            trace[0][j].F = g;
            g -= gap_extend;
        }

        for (size_t i = 1; i <= results[0].length(); ++i) {
            for (size_t j = 1; j <= strings[s].length(); ++j) {

                trace[i][j].E = std::max({
                    trace[i][j-1].E, trace[i][j-1].V - gap_open}) - gap_extend;

                trace[i][j].F = std::max({
                    trace[i-1][j].F, trace[i-1][j].V - gap_open}) - gap_extend;

                float max = std::numeric_limits<float>::min();
                for (size_t k = 0; k < strings.size(); ++k) {
                    char32_t results_char = results[k][i];

                    if (results_char == gap_char) { continue; }

                    std::u32string key = U"";
                    key += results_char + strings[s][j];
                    std::cout << convert(key) << "\n";
                    float value;
                    try {
                        value = weight.at(key);
                    } catch (std::out_of_range& e) {
                        std::stringstream err;
                        err << "Either '" << results_char << "' or '"
                            << strings[s][j-1] << "' are missing from the "
                            << "substitution table.";
                        throw std::invalid_argument(err.str());
                    }
                    max = value > max ? value : max;
                }
                trace[i][j].G = trace[i-1][j-1].G + max;

                trace[i][j].V = std::max({
                    trace[i][j].G,
                    trace[i][j].E,
                    trace[i][j].F,
                });
            }
        }

        // Trace-back
        size_t i = results[0].length();
        size_t j = strings[s].length();
        std::u32string new_string;

        std::vector<std::u32string> new_results;
        for (size_t k; k < results.size(); ++k) {
            new_results.push_back(U"");
        }

        while (i > 0 && j > 0) {
            Traceback cell = trace[i][j];

            if (cell.G >= cell.E && cell.G >= cell.F) {
                for (size_t k = 0; k < results.size(); ++k) {
                    new_results[k] += results[k][j];
                }
                new_string += strings[s][j];
                --i;
                --j;
            } else if (cell.E >= cell.G && cell.E >= cell.F) {
                for (size_t k = 0; k < results.size(); ++k) {
                    new_results[k] += gap_char;
                }
                new_string += strings[s][j];
                --j;
            } else {
                for (size_t k = 0; k < results.size(); ++k) {
                    new_results[k] += results[k][j];
                }
                new_string += gap_char;
                --i;
            }
        }
        results = new_results;
        results.push_back(new_string);
    }

    return results;
}


PYBIND11_MODULE(string_align, m) {
    m.doc() = "Align multiple strings.";
    m.def("align", &align, "Get the alignment string for a pair of strings.",
          py::arg("gap_open") = 5.0, py::arg("gap_extend") = 1.0);
    m.def("levenshtein", &levenshtein, "Get the levenshtein distance for 2 strings.");
    m.def("levenshtein_all", &levenshtein_all,
        "Get the levenshtein distance for all pairs of strings in the list.");
}


/*
<%
cfg['compiler_args'] = ['-std=c++17']
setup_pybind11(cfg)
%>
*/
