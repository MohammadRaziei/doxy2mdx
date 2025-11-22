import React from 'react';

// Member Title Component
export const MemberTitle = ({ permalink, title }) => {
  return (
    <h2 className="doxygen-memtitle">
      <span className="doxygen-permalink">
        <a href={permalink}>◆&nbsp;</a>
      </span>
      {title}
    </h2>
  );
};

// Member Item Component
export const MemberItem = ({ children }) => {
  return (
    <div className="doxygen-memitem">
      <div className="doxygen-memproto">
        {children}
      </div>
    </div>
  );
};

// Member Name Component
export const MemberName = ({ children }) => {
  return (
    <table className="doxygen-memname">
      <tbody>
        <tr>
          <td className="doxygen-memname">{children}</td>
        </tr>
      </tbody>
    </table>
  );
};

// Complete Member Definition Component
export const MemberDefinition = ({ 
  permalink, 
  title, 
  signature, 
  parameters = [],
  returnType,
  description,
  briefDescription 
}) => {
  return (
    <div className="doxygen-member-definition">
      <MemberTitle permalink={permalink} title={title} />
      
      <MemberItem>
        <MemberName>{signature}</MemberName>
      </MemberItem>
      
      <div className="doxygen-memdoc">
        {briefDescription && (
          <p className="doxygen-briefdescription">{briefDescription}</p>
        )}
        
        {description && (
          <div className="doxygen-detaileddescription">
            {description}
          </div>
        )}
        
        {parameters.length > 0 && (
          <dl className="doxygen-params">
            <dt>Parameters</dt>
            <dd>
              <table className="doxygen-params">
                <tbody>
                  {parameters.map((param, index) => (
                    <tr key={index}>
                      <td className="doxygen-paramname">{param.name}</td>
                      <td>{param.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </dd>
          </dl>
        )}
        
        {returnType && (
          <dl className="doxygen-section-return">
            <dt>Returns</dt>
            <dd>{returnType}</dd>
          </dl>
        )}
      </div>
    </div>
  );
};

// Section Component
export const Section = ({ title, children }) => {
  return (
    <div className="doxygen-section">
      <h2 className="doxygen-section-title">{title}</h2>
      {children}
    </div>
  );
};

// Code Block Component
export const CodeBlock = ({ language = 'cpp', code }) => {
  return (
    <div className="doxygen-programlisting">
      <pre className={`doxygen-highlight language-${language}`}>
        <code>{code}</code>
      </pre>
    </div>
  );
};

// Parameter List Component
export const ParameterList = ({ parameters }) => {
  return (
    <dl className="doxygen-params">
      <dt>Parameters</dt>
      <dd>
        <table className="doxygen-params">
          <tbody>
            {parameters.map((param, index) => (
              <tr key={index}>
                <td className="doxygen-paramname">{param.name}</td>
                <td>{param.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </dd>
    </dl>
  );
};

// Return Value Component
export const ReturnValue = ({ type }) => {
  return (
    <dl className="doxygen-section-return">
      <dt>Returns</dt>
      <dd><code>{type}</code></dd>
    </dl>
  );
};

// Main Doxygen Component
export const DoxygenComponent = ({ children }) => {
  return (
    <div className="doxygen-component">
      {children}
    </div>
  );
};

// Export all components as default
export default {
  MemberTitle,
  MemberItem,
  MemberName,
  MemberDefinition,
  Section,
  CodeBlock,
  ParameterList,
  ReturnValue,
  DoxygenComponent
};
