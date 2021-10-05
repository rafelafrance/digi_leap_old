
template<typename Iter>
std::string concat(Iter first, Iter last);

template<typename Iter>
std::string join(
    Iter first, Iter last,
    const std::string& separator = "",
    const std::string& conclude = "");
