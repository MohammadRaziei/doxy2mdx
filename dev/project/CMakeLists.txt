cmake_minimum_required(VERSION 3.16)
project(doxy2mdx LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(doxy2mdx_xml STATIC
    src/XmlParser.cpp
)
target_include_directories(doxy2mdx_xml PUBLIC include)

add_library(doxy2mdx_lib STATIC
    src/Config.cpp
    src/Converter.cpp
)
target_include_directories(doxy2mdx_lib PUBLIC include)
target_link_libraries(doxy2mdx_lib PUBLIC doxy2mdx_xml)

add_executable(doxy2mdx
    src/main.cpp
)
target_link_libraries(doxy2mdx PRIVATE doxy2mdx_lib)

if (MSVC)
    target_compile_options(doxy2mdx_xml PRIVATE /W4)
    target_compile_options(doxy2mdx_lib PRIVATE /W4)
    target_compile_options(doxy2mdx PRIVATE /W4)
else()
    target_compile_options(doxy2mdx_xml PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(doxy2mdx_lib PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(doxy2mdx PRIVATE -Wall -Wextra -Wpedantic)
endif()
