#!/usr/bin/env python3
"""
Main entry point for doxy2mdx - Convert Doxygen XML to MDX files for Docusaurus
"""

import argparse
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from .converter import DoxygenToMDXConverter


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file or use defaults"""
    default_config = {
        'input_xml_dir': 'docs/build/xml',
        'output_mdx_dir': 'docs/mdx',
        'css_output_path': 'docs/doxygen.css',
        'project_name': 'Project',
        'heading_offset': 0,
        'emit_index': True
    }
    
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f) or {}
        
        # Merge user config with defaults
        for key, value in user_config.items():
            if key in default_config:
                default_config[key] = value
    
    return default_config


def parse_args() -> Dict[str, Any]:
    """Parse command line arguments and return configuration"""
    parser = argparse.ArgumentParser(
        description='Convert Doxygen XML to MDX files for Docusaurus',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m doxy2mdx --input docs/xml --output docs/mdx
  python -m doxy2mdx --config config.yaml
  python -m doxy2mdx -i docs/xml -o docs/mdx --project "My Project"
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to YAML configuration file'
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Input directory containing Doxygen XML files'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for MDX files'
    )
    
    parser.add_argument(
        '--css',
        type=str,
        help='Output path for CSS file'
    )
    
    parser.add_argument(
        '--project',
        type=str,
        help='Project name for documentation'
    )
    
    parser.add_argument(
        '--heading-offset',
        type=int,
        help='Heading level offset (e.g., 1 to start from h2)'
    )
    
    parser.add_argument(
        '--no-index',
        action='store_true',
        help='Do not generate index file'
    )
    
    parser.add_argument(
        '--generate-css',
        action='store_true',
        help='Generate CSS file for styling'
    )
    
    args = parser.parse_args()
    
    # Load base configuration
    config = load_config(args.config)
    
    # Override with command line arguments
    if args.input:
        config['input_xml_dir'] = args.input
    
    if args.output:
        config['output_mdx_dir'] = args.output
    
    if args.css:
        config['css_output_path'] = args.css
    
    if args.project:
        config['project_name'] = args.project
    
    if args.heading_offset is not None:
        config['heading_offset'] = args.heading_offset
    
    if args.no_index:
        config['emit_index'] = False
    
    config['generate_css'] = args.generate_css
    
    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration and return True if valid"""
    input_dir = Path(config['input_xml_dir'])
    
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        return False
    
    if not input_dir.is_dir():
        print(f"Error: Input path is not a directory: {input_dir}")
        return False
    
    # Check if there are XML files in the input directory
    xml_files = list(input_dir.glob("*.xml"))
    if not xml_files:
        print(f"Warning: No XML files found in input directory: {input_dir}")
    
    return True


def generate_css_file(output_path: str):
    """Generate CSS file for styling doxygen elements"""
    css_content = """/* Doxygen to MDX CSS Styles */
.doxygen-table {
    border-collapse: collapse;
    width: 100%;
    margin: 1rem 0;
}

.doxygen-table th,
.doxygen-table td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}

.doxygen-table th {
    background-color: #f5f5f5;
    font-weight: bold;
}

.doxygen-table tr:nth-child(even) {
    background-color: #f9f9f9;
}

.doxygen-table tr:hover {
    background-color: #f0f0f0;
}

.doxygen-para {
    margin: 1rem 0;
    line-height: 1.6;
}

.doxygen-bold {
    font-weight: bold;
}

.doxygen-emphasis {
    font-style: italic;
}

.doxygen-computeroutput {
    font-family: 'Courier New', monospace;
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
}

.doxygen-ulink {
    color: #007bff;
    text-decoration: none;
}

.doxygen-ulink:hover {
    text-decoration: underline;
}

.doxygen-ref {
    color: #007bff;
    text-decoration: none;
}

.doxygen-ref:hover {
    text-decoration: underline;
}

.doxygen-programlisting {
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    margin: 1rem 0;
    overflow-x: auto;
}

.doxygen-codeline {
    font-family: 'Courier New', monospace;
    white-space: pre;
}

.doxygen-highlight {
    font-family: 'Courier New', monospace;
}

.doxygen-sectiondef {
    margin: 2rem 0;
}

.doxygen-memberdef {
    margin: 1.5rem 0;
    padding: 1rem;
    border-left: 4px solid #007bff;
    background-color: #f8f9fa;
}

.doxygen-param {
    margin: 0.5rem 0;
}

.doxygen-declname {
    font-weight: bold;
    font-family: 'Courier New', monospace;
}

.doxygen-defval {
    color: #6c757d;
    font-style: italic;
}

.doxygen-type {
    font-family: 'Courier New', monospace;
    color: #007bff;
}

.doxygen-name {
    font-weight: bold;
}

.doxygen-argsstring {
    font-family: 'Courier New', monospace;
    color: #6c757d;
}

.doxygen-briefdescription {
    color: #6c757d;
    font-style: italic;
    margin-bottom: 0.5rem;
}

.doxygen-detaileddescription {
    margin-top: 1rem;
}

.doxygen-includes {
    font-family: 'Courier New', monospace;
    background-color: #f5f5f5;
    padding: 0.5rem;
    border-radius: 3px;
    margin: 0.5rem 0;
}

.doxygen-innergroup {
    margin: 0.5rem 0;
}

/* Responsive design */
@media (max-width: 768px) {
    .doxygen-table {
        font-size: 0.9rem;
    }
    
    .doxygen-table th,
    .doxygen-table td {
        padding: 6px 8px;
    }
    
    .doxygen-memberdef {
        padding: 0.75rem;
    }
}
"""
    
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"CSS file generated: {output_path}")


def main():
    """Main entry point for doxy2mdx"""
    try:
        # Parse command line arguments
        config = parse_args()
        
        # Validate configuration
        if not validate_config(config):
            sys.exit(1)
        
        # Generate CSS file if requested
        if config.get('generate_css'):
            generate_css_file(config['css_output_path'])
        
        # Create converter and run conversion
        converter = DoxygenToMDXConverter(config)
        converter.convert_directory(
            config['input_xml_dir'],
            config['output_mdx_dir']
        )
        
        print(f"\nConversion completed successfully!")
        print(f"Input: {config['input_xml_dir']}")
        print(f"Output: {config['output_mdx_dir']}")
        
        if config.get('generate_css'):
            print(f"CSS: {config['css_output_path']}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
