import os
import pygixml
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
            doc = pygixml.parse_file(xml_file)
            root = doc.first_child()
            
            if not root:
                return None
                
            # Get compound name and kind
            compound = root.child('compounddef')
            if not compound:
                return None
                
            compound_name = compound.attribute('id') or ''
            compound_kind = compound.attribute('kind') or ''
            
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
    
    def _get_title(self, compound: pygixml.XMLNode) -> str:
        """Extract title from compound element"""
        title_elem = compound.child('title')
        if title_elem and title_elem.child_value():
            return title_elem.child_value().strip()
        
        # Fallback to compound name
        compound_name = compound.attribute('id') or ''
        return compound_name.replace('_', ' ').title()
    
    def _get_sidebar_label(self, compound: pygixml.XMLNode) -> str:
        """Generate sidebar label from compound"""
        title = self._get_title(compound)
        # Remove common prefixes and make it shorter
        label = re.sub(r'^(class|struct|namespace|file)\s+', '', title)
        return label
    
    def _render_compound(self, compound: pygixml.XMLNode) -> List[str]:
        """Render a compound definition to MDX lines"""
        lines = []
        
        # Add compound description
        brief_desc = compound.child('briefdescription')
        if brief_desc:
            brief_text = self._render_description(brief_desc)
            if brief_text:
                lines.extend([brief_text, ''])
        
        # Add detailed description
        detailed_desc = compound.child('detaileddescription')
        if detailed_desc:
            detailed_text = self._render_description(detailed_desc)
            if detailed_text:
                lines.extend([detailed_text, ''])
        
        # Add sections based on compound kind
        compound_kind = compound.attribute('kind') or ''
        
        if compound_kind in ['class', 'struct']:
            lines.extend(self._render_class_members(compound))
        elif compound_kind == 'namespace':
            lines.extend(self._render_namespace_members(compound))
        elif compound_kind == 'file':
            lines.extend(self._render_file_contents(compound))
        
        return lines
    
    def _render_description(self, description: pygixml.XMLNode) -> str:
        """Render a description element to markdown"""
        paragraphs = []
        
        # Find all para elements using XPath
        paras = description.select_nodes('.//para')
        for para in paras:
            para_text = self._render_paragraph(para)
            if para_text:
                paragraphs.append(para_text)
        
        return '\n\n'.join(paragraphs)
    
    def _render_paragraph(self, para: pygixml.XMLNode) -> str:
        """Render a paragraph element to markdown"""
        text_parts = []
        
        # Get text content using text() method
        text_content = para.text()
        if text_content:
            text_parts.append(text_content.strip())
        
        # Handle child elements
        for child in para:
            if child.name == 'computeroutput':
                text_parts.append(f'`{self._get_element_text(child)}`')
            elif child.name == 'bold':
                text_parts.append(f'**{self._get_element_text(child)}**')
            elif child.name == 'emphasis':
                text_parts.append(f'*{self._get_element_text(child)}*')
            elif child.name == 'ulink':
                url = child.attribute('url') or ''
                text_parts.append(f'[{self._get_element_text(child)}]({url})')
            elif child.name == 'ref':
                refid = child.attribute('refid') or ''
                text_parts.append(f'[{self._get_element_text(child)}](./{refid})')
            elif child.name == 'programlisting':
                code = self._render_code_block(child)
                text_parts.append(f'\n{code}\n')
            else:
                # Fallback to div for unknown elements
                text_parts.append(self._wrap_unknown_element(child))
        
        result = ' '.join(text_parts).strip()
        return result if result else ''
    
    def _render_code_block(self, programlisting: pygixml.XMLNode) -> str:
        """Render a code block to markdown"""
        code_lines = []
        
        # Find all codeline elements using XPath
        codelines = programlisting.select_nodes('.//codeline')
        for codeline in codelines:
            line_parts = []
            # Find all highlight elements in this codeline
            highlights = codeline.select_nodes('.//highlight')
            for highlight in highlights:
                text_content = highlight.text()
                if text_content:
                    line_parts.append(text_content)
            if line_parts:
                code_lines.append(''.join(line_parts))
        
        if code_lines:
            return f'```cpp\n' + '\n'.join(code_lines) + '\n```'
        return ''
    
    def _render_class_members(self, compound: pygixml.XMLNode) -> List[str]:
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
            # Find sectiondef elements with the specific kind
            sectiondefs = compound.select_nodes(f"sectiondef[@kind='{section_id}']")
            members = []
            for sectiondef in sectiondefs:
                members.extend(sectiondef.select_nodes('memberdef'))
            
            if members:
                lines.extend([
                    f'## {section_title}',
                    ''
                ])
                
                for member in members:
                    lines.extend(self._render_member(member))
                    lines.append('')
        
        return lines
    
    def _render_namespace_members(self, compound: pygixml.XMLNode) -> List[str]:
        """Render namespace members to MDX"""
        lines = []
        
        # Find all member definitions in the namespace
        members = compound.select_nodes('.//memberdef')
        if members:
            lines.extend([
                '## Members',
                ''
            ])
            
            for member in members:
                lines.extend(self._render_member(member))
                lines.append('')
        
        return lines
    
    def _render_file_contents(self, compound: pygixml.XMLNode) -> List[str]:
        """Render file contents to MDX"""
        lines = []
        
        # Add includes
        includes = compound.select_nodes('.//includes')
        if includes:
            lines.extend([
                '## Includes',
                ''
            ])
            for inc in includes:
                text_content = inc.text()
                if text_content:
                    lines.append(f'- `{text_content}`')
            lines.append('')
        
        # Add defined classes/structs
        innergroups = compound.select_nodes('.//innergroup')
        if innergroups:
            lines.extend([
                '## Defined Classes',
                ''
            ])
            for group in innergroups:
                refid = group.attribute('refid') or ''
                name = self._get_element_text(group)
                lines.append(f'- [{name}](./{refid})')
            lines.append('')
        
        return lines
    
    def _render_member(self, member: pygixml.XMLNode) -> List[str]:
        """Render a single member (function, variable, etc.) to MDX"""
        lines = []
        
        member_kind = member.attribute('kind') or ''
        member_name = member.child('name')
        if not member_name or not member_name.child_value():
            return lines
        
        name = member_name.child_value()
        
        # Create header based on member kind
        if member_kind == 'function':
            # Get function signature
            argsstring = member.child('argsstring')
            signature = f'{name}{argsstring.child_value() if argsstring else "()"}'
            lines.append(f'### `{signature}`')
        else:
            # Variable or other member
            lines.append(f'### `{name}`')
        
        lines.append('')
        
        # Add brief description
        brief_desc = member.child('briefdescription')
        if brief_desc:
            brief_text = self._render_description(brief_desc)
            if brief_text:
                lines.append(brief_text)
                lines.append('')
        
        # Add detailed description
        detailed_desc = member.child('detaileddescription')
        if detailed_desc:
            detailed_text = self._render_description(detailed_desc)
            if detailed_text:
                lines.append(detailed_text)
                lines.append('')
        
        # Add parameters for functions
        if member_kind == 'function':
            params = member.select_nodes('.//param')
            if params:
                lines.extend([
                    '#### Parameters',
                    ''
                ])
                for param in params:
                    param_name = param.child('declname')
                    param_desc = param.child('defval')
                    if param_name and param_name.child_value():
                        param_line = f'- `{param_name.child_value()}`'
                        if param_desc and param_desc.child_value():
                            param_line += f': {param_desc.child_value()}'
                        lines.append(param_line)
                lines.append('')
        
        # Add return value for functions
        if member_kind == 'function':
            returns = member.child('type')
            if returns and returns.child_value():
                lines.extend([
                    '#### Returns',
                    '',
                    f'`{returns.child_value().strip()}`',
                    ''
                ])
        
        return lines
    
    def _get_element_text(self, element: pygixml.XMLNode) -> str:
        """Extract text content from an element and its children"""
        return element.text() or ''
    
    def _wrap_unknown_element(self, element: pygixml.XMLNode) -> str:
        """Wrap unknown XML elements in div with doxygen- class"""
        element_text = self._get_element_text(element)
        if element_text:
            return f'<div class="doxygen-{element.name}">{element_text}</div>'
        return ''
