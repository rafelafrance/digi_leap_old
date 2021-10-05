#include <sstream>
#include <string>
#include <vector>

template<typename Iter>
std::string join(
    Iter first, Iter last,
    const std::string& separator = "",
    const std::string& ender = "")
{
    if (first == last) { return ender; }

    std::stringstream ss;
    ss << *first;
    ++first;

    while (first != last) {
        ss << separator;
        ss << *first;
        ++first;
    }

    ss << ender;

    return ss.str();
}


template<typename Iter>
std::string concat(Iter first, Iter last)
{
    if (first == last) { return ""; }

    std::stringstream ss;

    while (first != last) {
        ss << *first;
        ++first;
    }

    return ss.str();
}
