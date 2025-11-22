import React from 'react';

const MemberDefinition = ({ 
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
      <h2 className="doxygen-memtitle">
        <span className="doxygen-permalink">
          <a href={permalink}>◆&nbsp;</a>
        </span>
        {title}
      </h2>
      
      <div className="doxygen-memitem">
        <div className="doxygen-memproto">
          <table className="doxygen-memname">
            <tbody>
              <tr>
                <td className="doxygen-memname">{signature}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
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
    </div>
  );
};

export default MemberDefinition;
