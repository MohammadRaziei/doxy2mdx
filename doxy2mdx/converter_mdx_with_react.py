import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
import re


class DoxygenToMDXWithReactConverter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.heading_offset = config.get('heading_offset', 0)
        self.project_name = config.get('project_name', 'Project')
        self.components_path = config.get('components_path', './components/doxygen.jsx')
        
    def convert_directory(self, input_dir: str, output_dir: str):
        """Convert all XML files in input directory to MDX files with React components"""
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
        """Convert a single XML file to MDX content with React components"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Get compound definition
            compound = root.find('compounddef')
            if compound is None:
                return None
                
            compound_id = compound.get('id', '')
            compound_kind = compound.get('kind', '')
            
            # Start building MDX content with Mintlify structure
            mdx_lines = [
                '---',
                f'title: "{self._get_title(compound)}"',
                f'description: "{self._get_description(compound)}"',
                '---',
                '',
                'import React from \'react\';',
                f'import Doxygen from \'{self.components_path}\';',
                '',
                'export default function Documentation() {',
                '  return (',
                '    <div>'
            ]
            
            # Add compound description
            brief_desc = compound.find('briefdescription')
            if brief_desc is not None:
                brief_text = self._render_description(brief_desc)
                if brief_text:
                    mdx_lines.append(f'      <p className="doxygen-briefdescription">{brief_text}</p>')
            
            # Add detailed description
            detailed_desc = compound.find('detaileddescription')
            if detailed_desc is not None:
                detailed_text = self._render_description(detailed_desc)
                if detailed_text:
                    mdx_lines.append(f'      <div className="doxygen-detaileddescription">{detailed_text}</div>')
            
            # Add sections based on compound kind
            if compound_kind in ['class', 'struct']:
                mdx_lines.extend(self._render_class_members_mdx(compound))
            elif compound_kind == 'namespace':
                mdx_lines.extend(self._render_namespace_members_mdx(compound))
            elif compound_kind == 'file':
                mdx_lines.extend(self._render_file_contents_mdx(compound))
            
            mdx_lines.extend([
                '    </Doxygen.DoxygenComponent>',
                '  );',
                '}',
                ''
            ])
            
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
    
    def _get_description(self, compound: ET.Element) -> str:
        """Extract description from compound element"""
        brief_desc = compound.find('briefdescription')
        if brief_desc is not None:
            brief_text = self._render_description(brief_desc)
            if brief_text:
                return brief_text
        
        # Fallback to compound kind
        compound_kind = compound.get('kind', '')
        if compound_kind:
            return f"Documentation for {compound_kind}"
        return "Generated documentation"
    
    def _get_sidebar_label(self, compound: ET.Element) -> str:
        """Generate sidebar label from compound"""
        title = self._get_title(compound)
        # Remove common prefixes and make it shorter
        label = re.sub(r'^(class|struct|namespace|file)\s+', '', title)
        return label
    
    def _render_description(self, description: ET.Element) -> str:
        """Render a description element to text"""
        paragraphs = []
        
        # Find all para elements
        for para in description.findall('.//para'):
            para_text = self._render_paragraph_text(para)
            if para_text:
                paragraphs.append(para_text)
        
        return ' '.join(paragraphs)
    
    def _render_paragraph_text(self, para: ET.Element) -> str:
        """Render a paragraph element to plain text"""
        text_parts = []
        
        # Get text content
        if para.text:
            text_parts.append(para.text.strip())
        
        # Handle child elements
        for child in para:
            if child.tag in ['computeroutput', 'bold', 'emphasis']:
                text_parts.append(self._get_element_text(child))
            elif child.tag == 'ulink':
                text_parts.append(self._get_element_text(child))
            elif child.tag == 'ref':
                text_parts.append(self._get_element_text(child))
            else:
                text_parts.append(self._get_element_text(child))
            
            # Add tail text
            if child.tail:
                text_parts.append(child.tail.strip())
        
        result = ' '.join(text_parts).strip()
        return result if result else ''
    
    def _render_class_members_mdx(self, compound: ET.Element) -> List[str]:
        """Render class/struct members to MDX with React components"""
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
                lines.append(f'      <Doxygen.Section title="{section_title}">')
                
                for member in members:
                    lines.extend(self._render_member_mdx(member))
                
                lines.append('      </Doxygen.Section>')
        
        return lines
    
    def _render_namespace_members_mdx(self, compound: ET.Element) -> List[str]:
        """Render namespace members to MDX with React components"""
        lines = []
        
        # Find all member definitions in the namespace
        members = compound.findall('.//memberdef')
        if members:
            lines.append('      <Doxygen.Section title="Members">')
            
            for member in members:
                lines.extend(self._render_member_mdx(member))
            
            lines.append('      </Doxygen.Section>')
        
        return lines
    
    def _render_file_contents_mdx(self, compound: ET.Element) -> List[str]:
        """Render file contents to MDX with React components"""
        lines = []
        
        # Add includes
        includes = compound.findall('.//includes')
        if includes:
            lines.append('      <Doxygen.Section title="Includes">')
            lines.append('        <ul className="doxygen-includes">')
            for inc in includes:
                if inc.text:
                    lines.append(f'          <li><code>{inc.text}</code></li>')
            lines.append('        </ul>')
            lines.append('      </Doxygen.Section>')
        
        # Add defined classes/structs
        innergroups = compound.findall('.//innergroup')
        if innergroups:
            lines.append('      <Doxygen.Section title="Defined Classes">')
            lines.append('        <ul className="doxygen-innergroups">')
            for group in innergroups:
                refid = group.get('refid', '')
                name = self._get_element_text(group)
                lines.append(f'          <li><a href="./{refid}">{name}</a></li>')
            lines.append('        </ul>')
            lines.append('      </Doxygen.Section>')
        
        return lines
    
    def _render_member_mdx(self, member: ET.Element) -> List[str]:
        """Render a single member (function, variable, etc.) to MDX with React components"""
        lines = []
        
        member_kind = member.get('kind', '')
        member_name = member.find('name')
        if member_name is None or not member_name.text:
            return lines
        
        name = member_name.text
        
        # Prepare parameters
        parameters = []
        if member_kind == 'function':
            params = member.findall('.//param')
            for param in params:
                param_name = param.find('declname')
                if param_name is not None and param_name.text:
                    param_desc = param.find('defval')
                    desc_text = param_desc.text if param_desc is not None and param_desc.text else ''
                    parameters.append({
                        'name': param_name.text,
                        'description': desc_text
                    })
        
        # Prepare return type
        return_type = None
        if member_kind == 'function':
            returns = member.find('type')
            if returns is not None and returns.text:
                return_type = f'<code>{returns.text.strip()}</code>'
        
        # Prepare descriptions
        brief_desc = member.find('briefdescription')
        brief_text = self._render_description(brief_desc) if brief_desc is not None else ''
        
        detailed_desc = member.find('detaileddescription')
        detailed_text = self._render_description(detailed_desc) if detailed_desc is not None else ''
        
        # Prepare signature
        signature = name
        if member_kind == 'function':
            argsstring = member.find('argsstring')
            signature = f'{name}{argsstring.text if argsstring is not None and argsstring.text else "()"}'
        
        # Generate React component call
        member_id = member.get('id', '')
        lines.append(f'        <Doxygen.MemberDefinition')
        lines.append(f'          permalink="#{member_id}"')
        lines.append(f'          title="{name}"')
        lines.append(f'          signature="{signature}"')
        
        if parameters:
            lines.append(f'          parameters={{{parameters}}}')
        
        if return_type:
            lines.append(f'          returnType="{return_type}"')
        
        if brief_text:
            lines.append(f'          briefDescription="{brief_text}"')
        
        if detailed_text:
            lines.append(f'          description="{detailed_text}"')
        
        lines.append('        />')
        
        return lines
    
    def _get_element_text(self, element: ET.Element) -> str:
        """Extract text content from an element and its children"""
        text = element.text or ''
        for child in element:
            text += self._get_element_text(child)
            if child.tail:
                text += child.tail
        return text.strip()
