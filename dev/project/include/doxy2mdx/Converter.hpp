#pragma once

#include "Config.hpp"
#include "XmlParser.hpp"

#include <filesystem>
#include <string>
#include <vector>

namespace doxy2mdx {

class Converter {
public:
    explicit Converter(const Config& config);
    void run();

private:
    Config config_;

    void ensureOutputDir() const;
    void convertFile(const std::filesystem::path& path) const;
    std::string renderDocument(const XmlNode& root) const;
    std::string renderCompound(const XmlNode& compound) const;
    std::string renderMember(const XmlNode& member, int level) const;
    std::string renderDescription(const XmlNode& desc) const;
    std::string renderNodeInline(const XmlNode& node) const;
    std::string renderPara(const XmlNode& node) const;
    std::string renderTable(const XmlNode& node) const;
    std::string renderList(const XmlNode& node, const std::string& bullet) const;
    std::string renderCode(const XmlNode& node) const;
    std::string wrapUnknown(const XmlNode& node) const;
};

} // namespace doxy2mdx
