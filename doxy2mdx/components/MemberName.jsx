import React from 'react';

const MemberName = ({ children }) => {
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
