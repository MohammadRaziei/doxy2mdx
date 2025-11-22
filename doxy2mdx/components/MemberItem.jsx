import React from 'react';

const MemberItem = ({ children }) => {
  return (
    <div className="doxygen-memitem">
      <div className="doxygen-memproto">
        {children}
      </div>
    </div>
  );
};
