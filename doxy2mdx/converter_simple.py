import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
import re


class DoxygenToMDXConverter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.heading_offset = config.get('heading_offset', 0)
        self.project_name = config.get('project_name', 'Project')
        
    def convert_directory(self, input_dir: str, output_dir: str):
        """Convert all XML files in input directory to MDX files in output directory"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for xml_file in input_path.glob("*.xml"):
            if xml_file.name.startswith("index"):
                continue
                
            mdx_content = self.convert_file(str(xml_file))
            if mdx_content:
                output_file = output_path / f"{xml_file.stem}.mdx"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(mdx_content)
                print(f"Converted: {xml_file.name} -> {output_file.name}")
    
    def convert_file(self, xml_file: str) -> Optional[str]:
        """Convert a single XML file to MDX content"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Get compound definition
            compound = root.find('compounddef')
            if compound is None:
                return None
                
            compound_id = compound.get('id', '')
            compound_kind = compound.get('kind', '')
            
            # Start building MDX content
            mdx_lines = []
            
            # Add frontmatter for Docusaurus
            mdx_lines.extend([
                '---',
                f'title: {self._get_title(compound)}',
                f'sidebar_label: {self._get_sidebar_label(compound)}',
                '---',
                ''
            ])
            
            # Add main content
            mdx_lines.extend(self._render_compound(compound))
            
            return '\n'.join(mdx_lines)
            
        except Exception as e:
            print(f"Error parsing XML file {xml_file}: {e}")
            return None
    
    def _get_title(self, compound: ET.Element) -> str:
        """Extract title from compound element"""
        title_elem = compound.find('title')
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
        
        # Fallback to compound name
        compound_id = compound.get('id', '')
        if compound_id:
            return str(compound_id).replace('_', ' ').title()
        return 'Untitled'
    
    def _get_sidebar_label(self, compound: ET.Element) -> str:
        """Generate sidebar label from compound"""
        title = self._get_title(compound)
        # Remove common prefixes and make it shorter
        label = re.sub(r'^(class|struct|namespace|file)\s+', '', title)
        return label
    
    def _render_compound(self, compound: ET.Element) -> List[str]:
        """Render a compound definition to MDX lines"""
        lines = []
        
        # Add compound description
        brief_desc = compound.find('briefdescription')
        if brief_desc is not None:
            brief_text = self._render_description(brief_desc)
            if brief_text:
                lines.extend([brief_text, ''])
        
        # Add detailed description
        detailed_desc = compound.find('detaileddescription')
        if detailed_desc is not None:
            detailed_text = self._render_description(detailed_desc)
            if detailed_text:
                lines.extend([detailed_text, ''])
        
        # Add sections based on compound kind
        compound_kind = compound.get('kind', '')
        
        if compound_kind in ['class', 'struct']:
            lines.extend(self._render_class_members(compound))
        elif compound_kind == 'namespace':
            lines.extend(self._render_namespace_members(compound))
        elif compound_kind == 'file':
            lines.extend(self._render_file_contents(compound))
        
        return lines
    
    def _render_description(self, description: ET.Element) -> str:
        """Render a description element to markdown"""
        paragraphs = []
        
        # Find all para elements
        for para in description.findall('.//para'):
            para_text = self._render_paragraph(para)
            if para_text:
                paragraphs.append(para_text)
        
        return '\n\n'.join(paragraphs)
    
    def _render_paragraph(self, para: ET.Element) -> str:
        """Render a paragraph element to markdown"""
        text_parts = []
        
        # Get text content
        if para.text:
            text_parts.append(para.text.strip())
        
        # Handle child elements
        for child in para:
            if child.tag == 'computeroutput':
                text_parts.append(f'`{self._get_element_text(child)}`')
            elif child.tag == 'bold':
                text_parts.append(f'**{self._get_element_text(child)}**')
            elif child.tag == 'emphasis':
                text_parts.append(f'*{self._get_element_text(child)}*')
            elif child.tag == 'ulink':
                url = child.get('url', '')
                text_parts.append(f'[{self._get_element_text(child)}]({url})')
            elif child.tag == 'ref':
                refid = child.get('refid', '')
                text_parts.append(f'[{self._get_element_text(child)}](./{refid})')
            elif child.tag == 'programlisting':
                code = self._render_code_block(child)
                text_parts.append(f'\n{code}\n')
            else:
                # Fallback to div for unknown elements
                text_parts.append(self._wrap_unknown_element(child))
            
            # Add tail text
            if child.tail:
                text_parts.append(child.tail.strip())
        
        result = ' '.join(text_parts).strip()
        return result if result else ''
    
    def _render_code_block(self, programlisting: ET.Element) -> str:
        """Render a code block to markdown"""
        code_lines = []
        
        # Find all codeline elements
        for codeline in programlisting.findall('.//codeline'):
            line_parts = []
            # Find all highlight elements in this codeline
            for highlight in codeline.findall('.//highlight'):
                if highlight.text:
                    line_parts.append(highlight.text)
            if line_parts:
                code_lines.append(''.join(line_parts))
        
        if code_lines:
            return f'```cpp\n' + '\n'.join(code_lines) + '\n```'
        return ''
    
    def _render_class_members(self, compound: ET.Element) -> List[str]:
        """Render class/struct members to MDX"""
        lines = []
        
        sections = [
            ('public-attrib', 'Public Attributes'),
            ('public-func', 'Public Methods'),
            ('protected-attrib', 'Protected Attributes'),
            ('protected-func', 'Protected Methods'),
            ('private-attrib', 'Private Attributes'),
            ('private-func', 'Private Methods'),
        ]
        
        for section_id, section_title in sections:
            members = []
            for sectiondef in compound.findall(f"sectiondef[@kind='{section_id}']"):
                members.extend(sectiondef.findall('memberdef'))
            
            if members:
                lines.extend([
                    f'## {section_title}',
                    ''
                ])
                
                for member in members:
                    lines.extend(self._render_member(member))
                    lines.append('')
        
        return lines
    
    def _render_namespace_members(self, compound: ET.Element) -> List[str]:
        """Render namespace members to MDX"""
        lines = []
        
        # Find all member definitions in the namespace
        members = compound.findall('.//memberdef')
        if members:
            lines.extend([
                '## Members',
                ''
            ])
            
            for member in members:
                lines.extend(self._render_member(member))
                lines.append('')
        
        return lines
    
    def _render_file_contents(self, compound: ET.Element) -> List[str]:
        """Render file contents to MDX"""
        lines = []
        
        # Add includes
        includes = compound.findall('.//includes')
        if includes:
            lines.extend([
                '## Includes',
                ''
            ])
            for inc in includes:
                if inc.text:
                    lines.append(f'- `{inc.text}`')
            lines.append('')
        
        # Add defined classes/structs
        innergroups = compound.findall('.//innergroup')
        if innergroups:
            lines.extend([
                '## Defined Classes',
                ''
            ])
            for group in innergroups:
                refid = group.get('refid', '')
                name = self._get_element_text(group)
                lines.append(f'- [{name}](./{refid})')
            lines.append('')
        
        return lines
    
    def _render_member(self, member: ET.Element) -> List[str]:
        """Render a single member (function, variable, etc.) to MDX"""
        lines = []
        
        member_kind = member.get('kind', '')
        member_name = member.find('name')
        if member_name is None or not member_name.text:
            return lines
        
        name = member_name.text
        
        # Create header based on member kind
        if member_kind == 'function':
            # Get function signature
            argsstring = member.find('argsstring')
            signature = f'{name}{argsstring.text if argsstring is not None and argsstring.text else "()"}'
            lines.append(f'### `{signature}`')
        else:
            # Variable or other member
            lines.append(f'### `{name}`')
        
        lines.append('')
        
        # Add brief description
        brief_desc = member.find('briefdescription')
        if brief_desc is not None:
            brief_text = self._render_description(brief_desc)
            if brief_text:
                lines.append(brief_text)
                lines.append('')
        
        # Add detailed description
        detailed_desc = member.find('detaileddescription')
        if detailed_desc is not None:
            detailed_text = self._render_description(detailed_desc)
            if detailed_text:
                lines.append(detailed_text)
                lines.append('')
        
        # Add parameters for functions
        if member_kind == 'function':
            params = member.findall('.//param')
            if params:
                lines.extend([
                    '#### Parameters',
                    ''
                ])
                for param in params:
                    param_name = param.find('declname')
                    param_desc = param.find('defval')
                    if param_name is not None and param_name.text:
                        param_line = f'- `{param_name.text}`'
                        if param_desc is not None and param_desc.text:
                            param_line += f': {param_desc.text}'
                        lines.append(param_line)
                lines.append('')
        
        # Add return value for functions
        if member_kind == 'function':
            returns = member.find('type')
            if returns is not None and returns.text:
                lines.extend([
                    '#### Returns',
                    '',
                    f'`{returns.text.strip()}`',
                    ''
                ])
        
        return lines
    
    def _get_element_text(self, element: ET.Element) -> str:
        """Extract text content from an element and its children"""
        text = element.text or ''
        for child in element:
            text += self._get_element_text(child)
            if child.tail:
                text += child.tail
        return text.strip()
    
    def _wrap_unknown_element(self, element: ET.Element) -> str:
        """Wrap unknown XML elements in div with doxygen- class"""
        element_text = self._get_element_text(element)
        if element_text:
            return f'<div class="doxygen-{element.tag}">{element_text}</div>'
