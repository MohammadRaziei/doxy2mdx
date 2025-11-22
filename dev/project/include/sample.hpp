/**
 * @file sample.hpp
 * @brief Small example header to feed into Doxygen.
 */

#pragma once

#include <string>
#include <vector>

/**
 * @brief Represents a note inside a documentation example.
 */
struct Note {
    /// Title of the note.
    std::string title;

    /// Body of the note.
    std::string body;
};

/**
 * @brief Utility class for formatting text.
 */
class Formatter {
public:
    /**
     * @brief Join multiple lines into a single string.
     * @param lines Lines to join.
     * @param delimiter Text placed between each line.
     * @return Concatenated string.
     */
    static std::string join(const std::vector<std::string>& lines, const std::string& delimiter);

    /**
     * @brief Format a note as Markdown.
     * @param note Note instance.
     * @return Rendered text with a header and body.
     */
    std::string format(const Note& note) const;
};
