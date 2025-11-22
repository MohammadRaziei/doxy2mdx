import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
import re


class DoxygenToReactConverter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.heading_offset = config.get('heading_offset', 0)
        self.project_name = config.get('project_name', 'Project')
        
    def convert_directory(self, input_dir: str, output_dir: str):
        """Convert all XML files in input directory to React component files in output directory"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for xml_file in input_path.glob("*.xml"):
            if xml_file.name.startswith("index"):
                continue
                
            react_content = self.convert_file(str(xml_file))
            if react_content:
                output_file = output_path / f"{xml_file.stem}.jsx"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(react_content)
                print(f"Converted: {xml_file.name} -> {output_file.name}")
    
    def convert_file(self, xml_file: str) -> Optional[str]:
        """Convert a single XML file to React component content"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Get compound definition
            compound = root.find('compounddef')
            if compound is None:
                return None
                
            compound_id = compound.get('id', '')
            compound_kind = compound.get('kind', '')
            
            # Start building React component
            component_name = self._get_component_name(compound)
            
            react_lines = [
                'import React from \'react\';',
                '',
                f'const {component_name} = () => {{',
                '  return (',
                '    <div className="doxygen-component">'
            ]
            
            # Add compound description
            brief_desc = compound.find('briefdescription')
            if brief_desc is not None:
                brief_text = self._render_description(brief_desc)
                if brief_text:
                    react_lines.append(f'      <p className="doxygen-briefdescription">{brief_text}</p>')
            
            # Add detailed description
            detailed_desc = compound.find('detaileddescription')
            if detailed_desc is not None:
                detailed_text = self._render_description(detailed_desc)
                if detailed_text:
                    react_lines.append(f'      <div className="doxygen-detaileddescription">{detailed_text}</div>')
            
            # Add sections based on compound kind
            if compound_kind in ['class', 'struct']:
                react_lines.extend(self._render_class_members_react(compound))
            elif compound_kind == 'namespace':
                react_lines.extend(self._render_namespace_members_react(compound))
            elif compound_kind == 'file':
                react_lines.extend(self._render_file_contents_react(compound))
            
            react_lines.extend([
                '    </div>',
                '  );',
                '};',
                '',
                f'export default {component_name};',
                ''
            ])
            
            return '\n'.join(react_lines)
            
        except Exception as e:
            print(f"Error parsing XML file {xml_file}: {e}")
            return None
    
    def _get_component_name(self, compound: ET.Element) -> str:
        """Generate React component name from compound"""
        compound_id = compound.get('id', '')
        if compound_id:
            # Convert compound_id to PascalCase
            name = re.sub(r'[^a-zA-Z0-9]', ' ', compound_id)
            name = ''.join(word.capitalize() for word in name.split())
            return name
        return 'DoxygenComponent'
    
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
    
    def _render_class_members_react(self, compound: ET.Element) -> List[str]:
        """Render class/struct members to React JSX"""
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
                lines.append(f'      <h2 className="doxygen-section-title">{section_title}</h2>')
                
                for member in members:
                    lines.extend(self._render_member_react(member))
        
        return lines
    
    def _render_namespace_members_react(self, compound: ET.Element) -> List[str]:
        """Render namespace members to React JSX"""
        lines = []
        
        # Find all member definitions in the namespace
        members = compound.findall('.//memberdef')
        if members:
            lines.append('      <h2 className="doxygen-section-title">Members</h2>')
            
            for member in members:
                lines.extend(self._render_member_react(member))
        
        return lines
    
    def _render_file_contents_react(self, compound: ET.Element) -> List[str]:
        """Render file contents to React JSX"""
        lines = []
        
        # Add includes
        includes = compound.findall('.//includes')
        if includes:
            lines.append('      <h2 className="doxygen-section-title">Includes</h2>')
            lines.append('      <ul className="doxygen-includes">')
            for inc in includes:
                if inc.text:
                    lines.append(f'        <li><code>{inc.text}</code></li>')
            lines.append('      </ul>')
        
        # Add defined classes/structs
        innergroups = compound.findall('.//innergroup')
        if innergroups:
            lines.append('      <h2 className="doxygen-section-title">Defined Classes</h2>')
            lines.append('      <ul className="doxygen-innergroups">')
            for group in innergroups:
                refid = group.get('refid', '')
                name = self._get_element_text(group)
                lines.append(f'        <li><a href="./{refid}">{name}</a></li>')
            lines.append('      </ul>')
        
        return lines
    
    def _render_member_react(self, member: ET.Element) -> List[str]:
        """Render a single member (function, variable, etc.) to React JSX"""
        lines = []
        
        member_kind = member.get('kind', '')
        member_name = member.find('name')
        if member_name is None or not member_name.text:
            return lines
        
        name = member_name.text
        
        # Create member definition
        lines.append('      <div className="doxygen-member-definition">')
        
        # Add title with permalink
        member_id = member.get('id', '')
        lines.append(f'        <h3 className="doxygen-memtitle">')
        lines.append(f'          <span className="doxygen-permalink">')
        lines.append(f'            <a href="#{member_id}">◆&nbsp;</a>')
        lines.append(f'          </span>')
        lines.append(f'          {name}')
        lines.append(f'        </h3>')
        
        # Add signature
        if member_kind == 'function':
            argsstring = member.find('argsstring')
            signature = f'{name}{argsstring.text if argsstring is not None and argsstring.text else "()"}'
            lines.append(f'        <div className="doxygen-memitem">')
            lines.append(f'          <div className="doxygen-memproto">')
            lines.append(f'            <table className="doxygen-memname">')
            lines.append(f'              <tbody>')
            lines.append(f'                <tr>')
            lines.append(f'                  <td className="doxygen-memname">{signature}</td>')
            lines.append(f'                </tr>')
            lines.append(f'              </tbody>')
            lines.append(f'            </table>')
            lines.append(f'          </div>')
        
        # Add documentation
        lines.append('          <div className="doxygen-memdoc">')
        
        # Add brief description
        brief_desc = member.find('briefdescription')
        if brief_desc is not None:
            brief_text = self._render_description(brief_desc)
            if brief_text:
                lines.append(f'            <p className="doxygen-briefdescription">{brief_text}</p>')
        
        # Add detailed description
        detailed_desc = member.find('detaileddescription')
        if detailed_desc is not None:
            detailed_text = self._render_description(detailed_desc)
            if detailed_text:
                lines.append(f'            <div className="doxygen-detaileddescription">{detailed_text}</div>')
        
        # Add parameters for functions
        if member_kind == 'function':
            params = member.findall('.//param')
            if params:
                lines.append('            <dl className="doxygen-params">')
                lines.append('              <dt>Parameters</dt>')
                lines.append('              <dd>')
                lines.append('                <table className="doxygen-params">')
                lines.append('                  <tbody>')
                for param in params:
                    param_name = param.find('declname')
                    if param_name is not None and param_name.text:
                        param_desc = param.find('defval')
                        desc_text = param_desc.text if param_desc is not None and param_desc.text else ''
                        lines.append(f'                    <tr>')
                        lines.append(f'                      <td className="doxygen-paramname">{param_name.text}</td>')
                        lines.append(f'                      <td>{desc_text}</td>')
                        lines.append(f'                    </tr>')
                lines.append('                  </tbody>')
                lines.append('                </table>')
                lines.append('              </dd>')
                lines.append('            </dl>')
        
        # Add return value for functions
        if member_kind == 'function':
            returns = member.find('type')
            if returns is not None and returns.text:
                lines.append('            <dl className="doxygen-section-return">')
                lines.append('              <dt>Returns</dt>')
                lines.append(f'              <dd><code>{returns.text.strip()}</code></dd>')
                lines.append('            </dl>')
        
        lines.append('          </div>')
        
        if member_kind == 'function':
            lines.append('        </div>')
        
        lines.append('      </div>')
        
        return lines
    
    def _get_element_text(self, element: ET.Element) -> str:
        """Extract text content from an element and its children"""
        text = element.text or ''
        for child in element:
            text += self._get_element_text(child)
            if child.tail:
                text += child.tail
        return text.strip()
