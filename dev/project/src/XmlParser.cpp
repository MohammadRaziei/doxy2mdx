#include "doxy2mdx/XmlParser.hpp"

#include <cctype>
#include <fstream>
#include <sstream>
#include <stdexcept>

namespace doxy2mdx {

const XmlAttribute* XmlNode::attr(std::string_view key) const {
    for (const auto& a : attributes) {
        if (a.name == key) return &a;
    }
    return nullptr;
}

const XmlNode* XmlNode::child(std::string_view key) const {
    for (const auto& c : children) {
        if (c.name == key) return &c;
    }
    return nullptr;
}

std::vector<const XmlNode*> XmlNode::childrenNamed(std::string_view key) const {
    std::vector<const XmlNode*> result;
    for (const auto& c : children) {
        if (c.name == key) result.push_back(&c);
    }
    return result;
}

XmlParser::XmlParser(std::string_view input) : data_(input) {}

bool XmlParser::eof() const { return pos_ >= data_.size(); }

char XmlParser::peek() const { return eof() ? '\0' : data_[pos_]; }

char XmlParser::get() { return eof() ? '\0' : data_[pos_++]; }

bool XmlParser::startsWith(std::string_view s) const {
    return data_.substr(pos_, s.size()) == s;
}

void XmlParser::skipWhitespace() {
    while (!eof() && std::isspace(static_cast<unsigned char>(peek()))) {
        ++pos_;
    }
}

std::string XmlParser::parseName() {
    size_t start = pos_;
    while (!eof()) {
        char c = peek();
        if (std::isalnum(static_cast<unsigned char>(c)) || c == '_' || c == '-' || c == ':') {
            ++pos_;
        } else {
            break;
        }
    }
    return std::string(data_.substr(start, pos_ - start));
}

std::string XmlParser::parseUntil(std::string_view marker) {
    auto found = data_.find(marker, pos_);
    if (found == std::string::npos) {
        throw std::runtime_error("Unexpected end of XML while searching for marker");
    }
    auto start = pos_;
    pos_ = found;
    return std::string(data_.substr(start, found - start));
}

std::string XmlParser::decodeEntities(std::string_view text) const {
    std::string out;
    for (size_t i = 0; i < text.size(); ++i) {
        if (text[i] == '&') {
            if (text.substr(i, 4) == "&lt;") {
                out.push_back('<');
                i += 3;
            } else if (text.substr(i, 4) == "&gt;") {
                out.push_back('>');
                i += 3;
            } else if (text.substr(i, 5) == "&amp;") {
                out.push_back('&');
                i += 4;
            } else if (text.substr(i, 6) == "&quot;") {
                out.push_back('"');
                i += 5;
            } else if (text.substr(i, 6) == "&apos;") {
                out.push_back('\'');
                i += 5;
            } else {
                out.push_back('&');
            }
        } else {
            out.push_back(text[i]);
        }
    }
    return out;
}

XmlNode XmlParser::parseNode() {
    if (!startsWith("<")) {
        throw std::runtime_error("Expected '<' at position " + std::to_string(pos_));
    }
    get(); // consume '<'

    if (startsWith("!--")) {
        pos_ += 3;
        parseUntil("-->");
        pos_ += 3;
        skipWhitespace();
        return parseNode();
    }

    if (startsWith("![CDATA[")) {
        pos_ += 8;
        XmlNode node;
        node.name = "#text";
        node.text = parseUntil("]]>");
        pos_ += 3;
        return node;
    }

    std::string name = parseName();
    XmlNode node;
    node.name = name;

    skipWhitespace();
    while (!eof() && !startsWith(">") && !startsWith("/>")) {
        std::string attrName = parseName();
        skipWhitespace();
        if (get() != '=') {
            throw std::runtime_error("Expected '=' after attribute name");
        }
        skipWhitespace();
        char quote = get();
        if (quote != '"' && quote != '\'') {
            throw std::runtime_error("Expected quote for attribute value");
        }
        std::string value;
        while (!eof() && peek() != quote) {
            value.push_back(get());
        }
        if (get() != quote) {
            throw std::runtime_error("Unterminated attribute value");
        }
        node.attributes.push_back({attrName, decodeEntities(value)});
        skipWhitespace();
    }

    if (startsWith("/>")) {
        pos_ += 2;
        return node;
    }

    if (get() != '>') {
        throw std::runtime_error("Expected '>'");
    }

    std::string textBuffer;
    while (!eof()) {
        if (startsWith("</")) {
            pos_ += 2;
            std::string endName = parseName();
            if (endName != name) {
                throw std::runtime_error("Mismatched closing tag: " + endName + " for " + name);
            }
            skipWhitespace();
            if (get() != '>') {
                throw std::runtime_error("Expected '>' after closing tag");
            }
            break;
        }
        if (startsWith("<![CDATA[")) {
            if (!textBuffer.empty()) {
                node.children.push_back(XmlNode{"#text", decodeEntities(textBuffer), {}, {}});
                textBuffer.clear();
            }
            pos_ += 9;
            std::string cdata = parseUntil("]]>");
            pos_ += 3;
            node.children.push_back(XmlNode{"#text", cdata, {}, {}});
            continue;
        }
        if (startsWith("<!--")) {
            pos_ += 4;
            parseUntil("-->");
            pos_ += 3;
            continue;
        }
        if (startsWith("<")) {
            if (!textBuffer.empty()) {
                node.children.push_back(XmlNode{"#text", decodeEntities(textBuffer), {}, {}});
                textBuffer.clear();
            }
            node.children.push_back(parseNode());
        } else {
            textBuffer.push_back(get());
        }
    }
    if (!textBuffer.empty()) {
        node.children.push_back(XmlNode{"#text", decodeEntities(textBuffer), {}, {}});
    }

    return node;
}

XmlNode XmlParser::parse() {
    skipWhitespace();
    if (startsWith("<?")) {
        parseUntil("?>");
        pos_ += 2;
        skipWhitespace();
    }
    if (startsWith("<!DOCTYPE")) {
        parseUntil(">");
        get();
        skipWhitespace();
    }
    return parseNode();
}

XmlNode parseXmlFile(const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("Cannot open XML file: " + path);
    }
    std::ostringstream ss;
    ss << in.rdbuf();
    XmlParser parser(ss.str());
    return parser.parse();
}

} // namespace doxy2mdx
