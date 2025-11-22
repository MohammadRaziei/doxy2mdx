# Doxy2MDX

A Python tool to convert Doxygen XML output to MDX files for Docusaurus documentation.

## Overview

Doxy2MDX takes Doxygen-generated XML files and converts them into MDX format suitable for use with Docusaurus documentation sites. It preserves the structure and content of your C++ documentation while making it compatible with modern documentation platforms.

## Features

- **XML to MDX Conversion**: Convert Doxygen XML files to Docusaurus-compatible MDX
- **Flexible Configuration**: Support for both command-line arguments and YAML configuration files
- **CSS Styling**: Generate CSS files for styling doxygen elements with `doxygen-` prefixed classes
- **Markdown-Compatible**: Outputs clean markdown where possible, with div wrappers for complex elements
- **Docusaurus Integration**: Includes proper frontmatter for Docusaurus integration

## Installation

```bash
# Clone the repository
git clone https://github.com/mohammadraziei/doxy2mdx.git
cd doxy2mdx

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Convert XML files using default settings
python -m doxy2mdx --input docs/xml --output docs/mdx

# Generate CSS file along with conversion
python -m doxy2mdx --input docs/xml --output docs/mdx --generate-css

# Use a configuration file
python -m doxy2mdx --config config.yaml
```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--input` | `-i` | Input directory containing Doxygen XML files |
| `--output` | `-o` | Output directory for MDX files |
| `--config` | `-c` | Path to YAML configuration file |
| `--css` | | Output path for CSS file |
| `--project` | | Project name for documentation |
| `--heading-offset` | | Heading level offset (e.g., 1 to start from h2) |
| `--no-index` | | Do not generate index file |
| `--generate-css` | | Generate CSS file for styling |

### Configuration File

Create a `config.yaml` file:

```yaml
# Doxy2MDX Configuration File
input_xml_dir: docs/build/xml
output_mdx_dir: docs/mdx
css_output_path: docs/doxygen.css
project_name: "My C++ Project"
heading_offset: 1
emit_index: true
```

## Complete Workflow Example

### 1. Set up C++ Project Structure

```
dev/project/
├── include/
│   └── sample.hpp
├── src/
│   └── main.cpp
├── docs/
│   └── Doxyfile
└── CMakeLists.txt
```

### 2. Generate Doxygen XML

```bash
cd dev/project/docs
doxygen Doxyfile
```

### 3. Convert to MDX

```bash
# Using command line arguments
python -m doxy2mdx --input dev/project/build/xml --output dev/project/docs/mdx --generate-css

# Using configuration file
python -m doxy2mdx --config config.yaml
```

### 4. Use in Docusaurus

Add the generated MDX files to your Docusaurus documentation and include the CSS:

```jsx
// In your Docusaurus config
import './doxygen.css';
```

## Example Output

### Input XML (Doxygen)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<doxygen xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="compound.xsd" version="1.9.1" xml:lang="en-US">
  <compounddef id="sample_8hpp" kind="file">
    <compoundname>sample.hpp</compoundname>
    <includes local="no">string</includes>
    <includes local="no">vector</includes>
    <briefdescription>
      <para>Small example header to feed into Doxygen.</para>
    </briefdescription>
    <detaileddescription>
      <para>This is a sample header file for testing the doxy2mdx converter.</para>
    </detaileddescription>
    <location file="include/sample.hpp"/>
  </compounddef>
</doxygen>
```

### Output MDX (Docusaurus)

```mdx
---
title: Sample 8Hpp
sidebar_label: Sample 8Hpp
---

Small example header to feed into Doxygen.

This is a sample header file for testing the doxy2mdx converter.

## Includes

- `string`
- `vector`
```

## CSS Styling

The generated CSS file provides styling for doxygen elements with `doxygen-` prefixed classes:

```css
.doxygen-table {
    border-collapse: collapse;
    width: 100%;
    margin: 1rem 0;
}

.doxygen-programlisting {
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    margin: 1rem 0;
    overflow-x: auto;
}

.doxygen-memberdef {
    margin: 1.5rem 0;
    padding: 1rem;
    border-left: 4px solid #007bff;
    background-color: #f8f9fa;
}
```

## Project Structure

```
doxy2mdx/
├── doxy2mdx/
│   ├── __init__.py
│   ├── __main__.py          # Main entry point
│   ├── converter_simple.py  # XML to MDX converter
│   └── resources/
├── dev/
│   └── project/             # Sample C++ project
│       ├── include/
│       ├── src/
│       └── docs/
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.7+
- PyYAML
- Doxygen (for generating input XML)

## License

MIT License - see LICENSE.txt for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Acknowledgments

Inspired by doxybook2 and similar tools for converting Doxygen output to modern documentation formats.
