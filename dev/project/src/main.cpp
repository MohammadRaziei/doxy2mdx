#include "doxy2mdx/Config.hpp"
#include "doxy2mdx/Converter.hpp"

#include <exception>
#include <iostream>

int main(int argc, char** argv) {
    try {
        auto cfg = doxy2mdx::applyCliArgs(argc, argv);
        doxy2mdx::Converter converter(cfg);
        converter.run();
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
