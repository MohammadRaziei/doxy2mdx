#include "doxy2mdx/Config.hpp"

#include <cctype>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>

namespace fs = std::filesystem;

namespace doxy2mdx {

std::string loadFile(const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("Unable to read file: " + path);
    }
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

std::unordered_map<std::string, std::string> parseYamlLike(const std::string& content) {
    std::unordered_map<std::string, std::string> kv;
    std::istringstream ss(content);
    std::string line;
    while (std::getline(ss, line)) {
        auto hash = line.find('#');
        if (hash != std::string::npos) {
            line = line.substr(0, hash);
        }
        auto colon = line.find(':');
        if (colon == std::string::npos) {
            continue;
        }
        std::string key = line.substr(0, colon);
        std::string value = line.substr(colon + 1);
        auto ltrim = [](std::string& s) {
            size_t pos = 0;
            while (pos < s.size() && std::isspace(static_cast<unsigned char>(s[pos]))) {
                ++pos;
            }
            s.erase(0, pos);
        };
        auto rtrim = [](std::string& s) {
            size_t pos = s.size();
            while (pos > 0 && std::isspace(static_cast<unsigned char>(s[pos - 1]))) {
                --pos;
            }
            s.erase(pos);
        };
        ltrim(key);
        rtrim(key);
        ltrim(value);
        rtrim(value);
        if (!key.empty()) {
            kv[key] = value;
        }
    }
    return kv;
}

Config parseConfig(const std::unordered_map<std::string, std::string>& kv) {
    Config cfg;
    cfg.inputXmlDir = "docs/build/xml";
    cfg.outputMdxDir = "docs/mdx";
    cfg.cssOutputPath = "docs/doxygen.css";
    cfg.projectName = "Project";
    cfg.headingOffset = 0;
    cfg.emitIndex = true;

    auto find = [&](const std::string& key) -> const std::string* {
        auto it = kv.find(key);
        if (it == kv.end()) {
            return nullptr;
        }
        return &it->second;
    };

    if (auto v = find("input")) cfg.inputXmlDir = *v;
    if (auto v = find("output")) cfg.outputMdxDir = *v;
    if (auto v = find("css")) cfg.cssOutputPath = *v;
    if (auto v = find("project")) cfg.projectName = *v;
    if (auto v = find("heading_offset")) cfg.headingOffset = std::stoi(*v);
    if (auto v = find("emit_index")) cfg.emitIndex = (*v != "false");

    return cfg;
}

Config applyCliArgs(int argc, char** argv) {
    Config cfg = parseConfig({});

    auto applyKv = [&](const std::unordered_map<std::string, std::string>& kv) {
        cfg = parseConfig(kv);
    };

    std::unordered_map<std::string, std::string> yamlKv;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        auto requireValue = [&](const std::string& flag) -> std::string {
            if (i + 1 >= argc) {
                throw std::runtime_error("Flag " + flag + " requires a value");
            }
            return std::string(argv[++i]);
        };

        if (arg == "--help" || arg == "-h") {
            std::cout << "doxy2mdx - Convert Doxygen XML to MDX\n"
                      << "Usage: doxy2mdx [--config file] [--input dir] [--output dir] [--css path]\n"
                      << "                [--project name] [--heading-offset n] [--no-index]\n";
            std::exit(0);
        } else if (arg == "--config") {
            auto path = requireValue(arg);
            yamlKv = parseYamlLike(loadFile(path));
            applyKv(yamlKv);
        } else if (arg == "--input" || arg == "-i") {
            cfg.inputXmlDir = requireValue(arg);
        } else if (arg == "--output" || arg == "-o") {
            cfg.outputMdxDir = requireValue(arg);
        } else if (arg == "--css") {
            cfg.cssOutputPath = requireValue(arg);
        } else if (arg == "--project") {
            cfg.projectName = requireValue(arg);
        } else if (arg == "--heading-offset") {
            cfg.headingOffset = std::stoi(requireValue(arg));
        } else if (arg == "--no-index") {
            cfg.emitIndex = false;
        } else {
            throw std::runtime_error("Unknown argument: " + arg);
        }
    }

    return cfg;
}

} // namespace doxy2mdx
