#pragma once

#include <optional>
#include <string>
#include <unordered_map>

namespace doxy2mdx {

struct Config {
    std::string inputXmlDir;
    std::string outputMdxDir;
    std::string cssOutputPath;
    std::string projectName;
    int headingOffset = 0;
    bool emitIndex = true;
};

std::string loadFile(const std::string& path);

Config parseConfig(const std::unordered_map<std::string, std::string>& kv);

std::unordered_map<std::string, std::string> parseYamlLike(const std::string& content);

Config applyCliArgs(int argc, char** argv);

} // namespace doxy2mdx
