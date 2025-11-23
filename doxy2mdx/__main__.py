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

from .converter_simple import DoxygenToMDXConverter
from .converter_mdx_with_react import DoxygenToMDXWithReactConverter
from .converter_react import DoxygenToReactConverter


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file or use defaults"""
    default_config = {
        'input_xml_dir': './xml',
        'output_mdx_dir': './mdx',
        'css_output_path': './doxygen.css',
        'project_name': 'Project',
        'heading_offset': 0,
        'emit_index': True,
        'mode': 'simple',  # simple, react, raw
        'components_path': './components/doxygen.jsx'
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
Conversion Modes:
  simple    - Basic MDX output (default)
  react     - MDX with embedded React components
  raw       - Pure React components (.jsx files)

Examples:
  python -m doxy2mdx --input docs/xml --output docs/mdx
  python -m doxy2mdx --config config.yaml
  python -m doxy2mdx -i docs/xml -o docs/mdx --mode react
  python -m doxy2mdx -i docs/xml -o docs/components --mode raw
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
    
    parser.add_argument(
        '--mode',
        choices=['simple', 'react', 'raw'],
        default='simple',
        help='Conversion mode: simple (basic MDX), react (MDX with React), raw (pure React)'
    )
    
    parser.add_argument(
        '--components-path',
        type=str,
        help='Path to React components file (for react mode)'
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
    config['mode'] = args.mode
    
    if args.components_path:
        config['components_path'] = args.components_path
    
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
:root {
  --doxygen-accent: #0f766e;
  --doxygen-muted: #6b7280;
  --doxygen-border: #e5e7eb;
  --doxygen-bg: #f9fafb;
  --doxygen-code: #0b1021;
}

.doxygen-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.doxygen-table th,
.doxygen-table td {
  border: 1px solid var(--doxygen-border);
  padding: 0.5rem 0.75rem;
}

.doxygen-programlisting {
  background: var(--doxygen-bg);
  border: 1px solid var(--doxygen-border);
  padding: 0.75rem;
  border-radius: 6px;
  overflow-x: auto;
}

.doxygen-para {
  margin: 0.5rem 0;
}

.doxygen-unknown {
  border-left: 3px solid var(--doxygen-accent);
  padding-left: 0.75rem;
  color: var(--doxygen-muted);
}

.doxygen-member-definition {
  margin: 1.5rem 0;
  padding: 1rem;
  border-left: 4px solid var(--doxygen-accent);
  background-color: var(--doxygen-bg);
}

.doxygen-memtitle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.doxygen-permalink a {
  color: var(--doxygen-accent);
  text-decoration: none;
  font-weight: bold;
}

.doxygen-memitem {
  margin: 1rem 0;
}

.doxygen-memproto {
  background: white;
  border: 1px solid var(--doxygen-border);
  border-radius: 4px;
  padding: 0.75rem;
}

.doxygen-memname {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.doxygen-memdoc {
  margin-top: 1rem;
  padding-left: 1rem;
  border-left: 2px solid var(--doxygen-border);
}

.doxygen-briefdescription {
  color: var(--doxygen-muted);
  font-style: italic;
  margin-bottom: 0.5rem;
}

.doxygen-detaileddescription {
  margin: 1rem 0;
  line-height: 1.6;
}

.doxygen-params {
  margin: 1rem 0;
}

.doxygen-params table {
  width: 100%;
  border-collapse: collapse;
}

.doxygen-paramname {
  font-weight: bold;
  font-family: 'Courier New', monospace;
  padding-right: 1rem;
}

.doxygen-section-return {
  margin: 1rem 0;
  padding: 0.75rem;
  background: var(--doxygen-bg);
  border-radius: 4px;
}

.doxygen-section-title {
  color: var(--doxygen-accent);
  border-bottom: 2px solid var(--doxygen-border);
  padding-bottom: 0.5rem;
  margin: 2rem 0 1rem 0;
}

.doxygen-section {
  margin: 2rem 0;
}

.doxygen-component {
  max-width: 100%;
}

/* Responsive design */
@media (max-width: 768px) {
  .doxygen-table {
    font-size: 0.9rem;
  }
  
  .doxygen-table th,
  .doxygen-table td {
    padding: 0.25rem 0.5rem;
  }
  
  .doxygen-member-definition {
    padding: 0.75rem;
  }
  
  .doxygen-memproto {
    padding: 0.5rem;
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
        
        # Select converter based on mode
        mode = config.get('mode', 'simple')
        print(f"Using conversion mode: {mode}")
        
        if mode == 'react':
            converter = DoxygenToMDXWithReactConverter(config)
            output_ext = '.mdx'
        elif mode == 'raw':
            converter = DoxygenToReactConverter(config)
            output_ext = '.jsx'
        else:  # simple mode
            converter = DoxygenToMDXConverter(config)
            output_ext = '.mdx'
        
        # Run conversion
        converter.convert_directory(
            config['input_xml_dir'],
            config['output_mdx_dir']
        )
        
        print(f"\n✅ Conversion completed successfully!")
        print(f"Mode: {mode}")
        print(f"Input: {config['input_xml_dir']}")
        print(f"Output: {config['output_mdx_dir']} ({output_ext} files)")
        
        if config.get('generate_css'):
            print(f"CSS: {config['css_output_path']}")
        
        if mode == 'react':
            print(f"Components: {config.get('components_path', './components/doxygen.jsx')}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()