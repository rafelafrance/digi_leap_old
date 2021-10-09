// cppimport

/*
    Naive implementations based on Gusfield 1997
*/


#include <algorithm>
#include <codecvt>
#include <cstddef>
#include <exception>
#include <iostream>
#include <iterator>
#include <locale>
#include <numeric>
#include <sstream>
#include <tuple>
#include <utility>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

const char32_t gap = U'⋄';


typedef std::tuple<long, std::u32string, std::u32string, long> Alignment;
typedef std::tuple<long, std::u32string, std::u32string> Result;
typedef std::vector<Alignment> Alignments;
typedef std::vector<Result> Results;


struct Traceback {
    long score;
    bool up;
    bool diag;
    bool left;
    Traceback(): score(0), up(false), diag{false}, left(false) {}
};

typedef std::vector<std::vector<Traceback>> TraceMatrix;


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


long count_gaps(const std::u32string& str) {
    long end = str.length() - 1;
    long gaps = 0;

    for (unsigned long i = 1; i < str.length(); ++i) {
        gaps += (str[i-1] == gap && str[i] != gap) ? 1 : 0;
    }
    gaps += (str[end-1] != gap && str[end] == gap) ? 1 : 0;

    return gaps;
}


void backtrace(
    TraceMatrix &trace,
    const long row,
    const long col,
    const std::u32string &in1,
    const std::u32string &in2,
    std::u32string out1,
    std::u32string out2,
    Alignments &aligns,
    long score)
{
    if (row <= 0 && col <= 0) {
        std::reverse(out1.begin(), out1.end());
        std::reverse(out2.begin(), out2.end());
        long gaps = count_gaps(out1) + count_gaps(out2);
        Alignment a = std::tuple(score, out1, out2, gaps);
        aligns.push_back(a);
    }

    Traceback cell = trace[row][col];

    if (cell.diag){
        backtrace(
            trace,
            row-1,
            col-1,
            in1,
            in2,
            out1+in1[row-1],
            out2+in2[col-1],
            aligns,
            score);
    }
    if (cell.left) {
        backtrace(
            trace,
            row,
            col-1,
            in1,
            in2,
            out1+gap,
            out2+in2[col-1],
            aligns,
            score);
    }
    if (cell.up) {
        backtrace(
            trace,
            row-1,
            col,
            in1,
            in2,
            out1+in1[row-1],
            out2+gap,
            aligns,
            score);
    }
}


Results align(std::u32string& str1, std::u32string& str2) {
    const long len1 = str1.length();
    const long len2 = str2.length();

    TraceMatrix trace(len1+1, std::vector<Traceback>(len2+1));

    for (long r = 1; r <= len1; ++r) {
        trace[r][0].score = r;
        trace[r][0].up = true;
    }

    for (long c = 1; c <= len2; ++c) {
        trace[0][c].score = c;
        trace[0][c].left = true;
    }

    for (long r = 1; r <= len1; ++r) {
        for (long c = 1; c <= len2; ++c) {
            long up = trace[r-1][c].score + 1;
            long left = trace[r][c-1].score + 1;
            long diag = trace[r-1][c-1].score + (str1[r-1] == str2[c-1] ? 0 : 1);

            if (up <= left && up <= diag) {
                trace[r][c].score = up;
                trace[r][c].up = true;
            }

            if (left <= up && left <= diag) {
                trace[r][c].score = left;
                trace[r][c].left = true;
            }

            if (diag <= up && diag <= left) {
                trace[r][c].score = diag;
                trace[r][c].diag = true;
            }
        }
    }

    Alignments aligns;
    Results results;

    backtrace(trace, len1, len2, str1, str2, U"", U"", aligns, trace[len1][len2].score);

    std::stable_sort(begin(aligns), end(aligns),
        [](auto const &a1, auto const &a2) {
            return std::get<0>(a1) < std::get<0>(a2);
        });

    long gaps = std::get<3>(aligns[0]);
    for (auto a : aligns) {
        if (std::get<3>(a) != gaps) {
            break;
        }
        Result result = std::make_tuple(std::get<0>(a), std::get<1>(a), std::get<2>(a));
        results.push_back(result);
    }

    return results;
}


PYBIND11_MODULE(string_align, m) {
    m.doc() = "Align multiple strings.";
    m.def("align", &align, "Get the alignment string for a pair of strings.");
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
