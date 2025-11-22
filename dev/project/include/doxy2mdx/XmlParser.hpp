#pragma once

#include <string>
#include <string_view>
#include <vector>

namespace doxy2mdx {

struct XmlAttribute {
    std::string name;
    std::string value;
};

struct XmlNode {
    std::string name;
    std::string text;
    std::vector<XmlAttribute> attributes;
    std::vector<XmlNode> children;

    const XmlAttribute* attr(std::string_view key) const;
    const XmlNode* child(std::string_view key) const;
    std::vector<const XmlNode*> childrenNamed(std::string_view key) const;
};

class XmlParser {
public:
    explicit XmlParser(std::string_view input);
    XmlNode parse();

private:
    std::string_view data_;
    size_t pos_ = 0;

    void skipWhitespace();
    bool startsWith(std::string_view s) const;
    bool eof() const;
    char peek() const;
    char get();
    std::string parseName();
    std::string parseUntil(std::string_view marker);
    std::string decodeEntities(std::string_view text) const;
    XmlNode parseNode();
};

XmlNode parseXmlFile(const std::string& path);

} // namespace doxy2mdx
