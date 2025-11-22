#include "doxy2mdx/Converter.hpp"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <unordered_map>

namespace fs = std::filesystem;

namespace doxy2mdx {

namespace {
std::string heading(int level, int offset) {
    int l = level + offset;
    if (l < 1) l = 1;
    if (l > 6) l = 6;
    return std::string(static_cast<size_t>(l), '#');
}

std::string nodeText(const XmlNode& node) {
    std::string out;
    if (node.name == "#text") {
        return node.text;
    }
    for (const auto& c : node.children) {
        out += nodeText(c);
    }
    return out;
}
} // namespace

Converter::Converter(const Config& config) : config_(config) {}

void Converter::run() {
    ensureOutputDir();
    std::vector<std::string> generated;

    for (auto& entry : fs::recursive_directory_iterator(config_.inputXmlDir)) {
        if (!entry.is_regular_file() || entry.path().extension() != ".xml") continue;
        convertFile(entry.path());
        generated.push_back(entry.path().stem().string() + ".mdx");
    }

    if (config_.emitIndex && !generated.empty()) {
        std::ofstream out(fs::path(config_.outputMdxDir) / "index.mdx");
        out << "# " << config_.projectName << "\n\n";
        for (const auto& file : generated) {
            out << "- [" << file << "](./" << file << ")\n";
        }
    }
}

void Converter::ensureOutputDir() const {
    fs::create_directories(config_.outputMdxDir);
}

void Converter::convertFile(const fs::path& path) const {
    XmlNode root = parseXmlFile(path.string());
    std::string mdx = renderDocument(root);
    fs::path outPath = fs::path(config_.outputMdxDir) / path.stem();
    outPath.replace_extension(".mdx");
    std::ofstream out(outPath);
    if (!out) {
        throw std::runtime_error("Cannot write to " + outPath.string());
    }
    out << mdx;
}

std::string Converter::renderDocument(const XmlNode& root) const {
    std::ostringstream out;
    if (root.name == "doxygen") {
        for (const auto* comp : root.childrenNamed("compounddef")) {
            out << renderCompound(*comp) << "\n";
        }
    } else if (root.name == "compounddef") {
        out << renderCompound(root);
    } else {
        out << wrapUnknown(root);
    }
    return out.str();
}

std::string Converter::renderCompound(const XmlNode& compound) const {
    std::ostringstream out;
    std::string name = compound.child("compoundname") ? nodeText(*compound.child("compoundname")) : "Unknown";
    std::string kind = "compound";
    if (auto* k = compound.attr("kind")) kind = k->value;

    out << heading(1, config_.headingOffset) << " " << name << " (" << kind << ")\n\n";

    if (auto* brief = compound.child("briefdescription")) {
        out << renderDescription(*brief);
    }
    if (auto* detail = compound.child("detaileddescription")) {
        out << renderDescription(*detail);
    }

    for (const auto* section : compound.childrenNamed("sectiondef")) {
        std::string stitle = section->attr("kind") ? section->attr("kind")->value : "Members";
        out << "\n" << heading(2, config_.headingOffset) << " " << stitle << "\n\n";
        for (const auto& member : section->children) {
            if (member.name == "memberdef") {
                out << renderMember(member, 3);
            }
        }
    }
    return out.str();
}

std::string Converter::renderMember(const XmlNode& member, int level) const {
    std::ostringstream out;
    std::string name = member.child("name") ? nodeText(*member.child("name")) : "member";
    std::string def = member.child("definition") ? nodeText(*member.child("definition")) : "";
    std::string args = member.child("argsstring") ? nodeText(*member.child("argsstring")) : "";
    std::string signature = def.empty() ? name : def + args;

    out << heading(level, config_.headingOffset) << " " << signature << "\n\n";

    if (auto* brief = member.child("briefdescription")) {
        out << renderDescription(*brief);
    }
    if (auto* detail = member.child("detaileddescription")) {
        out << renderDescription(*detail);
    }

    return out.str();
}

std::string Converter::renderDescription(const XmlNode& desc) const {
    std::ostringstream out;
    for (const auto& child : desc.children) {
        if (child.name == "para") {
            out << renderPara(child) << "\n\n";
        } else if (child.name == "#text") {
            if (!child.text.empty()) out << child.text << "\n\n";
        } else {
            out << wrapUnknown(child) << "\n\n";
        }
    }
    return out.str();
}

std::string Converter::renderPara(const XmlNode& node) const {
    std::ostringstream out;
    for (const auto& child : node.children) {
        out << renderNodeInline(child);
    }
    return out.str();
}

std::string Converter::renderTable(const XmlNode& node) const {
    std::vector<std::vector<std::string>> rows;
    for (const auto& row : node.children) {
        if (row.name != "row") continue;
        std::vector<std::string> cells;
        for (const auto& entry : row.children) {
            if (entry.name == "entry") {
                std::ostringstream cell;
                for (const auto& c : entry.children) {
                    cell << renderNodeInline(c);
                }
                cells.push_back(cell.str());
            }
        }
        if (!cells.empty()) rows.push_back(std::move(cells));
    }
    if (rows.empty()) return "";
    std::ostringstream out;
    out << "<table class=\"doxygen-table\">\n";
    for (size_t r = 0; r < rows.size(); ++r) {
        out << "<tr>";
        const bool header = (r == 0);
        for (const auto& cell : rows[r]) {
            out << (header ? "<th>" : "<td>") << cell << (header ? "</th>" : "</td>");
        }
        out << "</tr>\n";
    }
    out << "</table>\n";
    return out.str();
}

std::string Converter::renderList(const XmlNode& node, const std::string& bullet) const {
    std::ostringstream out;
    for (const auto& item : node.children) {
        if (item.name != "listitem") continue;
        out << bullet << " ";
        for (const auto& c : item.children) {
            if (c.name == "para") {
                out << renderPara(c);
            } else {
                out << renderNodeInline(c);
            }
        }
        out << "\n";
    }
    return out.str();
}

std::string Converter::renderCode(const XmlNode& node) const {
    std::ostringstream out;
    out << "```cpp\n";
    for (const auto& cl : node.children) {
        if (cl.name != "codeline") continue;
        for (const auto& c : cl.children) {
            out << renderNodeInline(c);
        }
        out << "\n";
    }
    out << "```\n";
    return out.str();
}

std::string Converter::renderNodeInline(const XmlNode& node) const {
    if (node.name == "#text") {
        return node.text;
    }
    if (node.name == "bold") {
        return "**" + nodeText(node) + "**";
    }
    if (node.name == "emphasis") {
        return "*" + nodeText(node) + "*";
    }
    if (node.name == "computeroutput") {
        return "`" + nodeText(node) + "`";
    }
    if (node.name == "ref") {
        std::string label = nodeText(node);
        std::string anchor = label;
        if (auto* id = node.attr("refid")) anchor = id->value;
        return "[" + label + "](#" + anchor + ")";
    }
    if (node.name == "itemizedlist") {
        return "\n" + renderList(node, "-") + "\n";
    }
    if (node.name == "orderedlist") {
        return "\n" + renderList(node, "1.") + "\n";
    }
    if (node.name == "table") {
        return "\n" + renderTable(node) + "\n";
    }
    if (node.name == "programlisting") {
        return "\n" + renderCode(node) + "\n";
    }
    if (node.name == "para") {
        return renderPara(node);
    }
    return wrapUnknown(node);
}

std::string Converter::wrapUnknown(const XmlNode& node) const {
    std::ostringstream out;
    out << "<div class=\"doxygen-" << node.name << "\">";
    for (const auto& c : node.children) {
        out << renderNodeInline(c);
    }
    out << "</div>";
    return out.str();
}

} // namespace doxy2mdx
