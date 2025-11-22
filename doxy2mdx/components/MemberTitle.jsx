import React from 'react';

const MemberTitle = ({ permalink, title }) => {
  return (
    <h2 className="doxygen-memtitle">
      <span className="doxygen-permalink">
        <a href={permalink}>◆&nbsp;</a>
      </span>
      {title}
    </h2>
  );
};
