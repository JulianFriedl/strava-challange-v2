import React, { useState, Children } from 'react';
import styled, { keyframes } from 'styled-components';
import websitePalette from '../../styles/palette';

// Animation for expanding/collapsing
const expandAnimation = keyframes`
  from {
    max-height: 0;
    opacity: 0;
  }
  to {
    max-height: 500px; // Arbitrary large max-height
    opacity: 1;
  }
`;

const collapseAnimation = keyframes`
  from {
    max-height: 500px;
    opacity: 1;
  }
  to {
    max-height: 0;
    opacity: 0;
  }
`;

const ExpandableContainer = styled.div`
  overflow: hidden;
  animation: ${({ isExpanded }) => isExpanded ? expandAnimation : collapseAnimation} 0.5s ease forwards;
`;

const ToggleButton = styled.button`
  // Style your toggle button
  background: ${websitePalette.secondary};
  color: white;
  border: none;
  cursor: pointer;
  padding: 10px;
  width: 100%;
`;

export default function ExpandableComponent({ children, label }) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Prevent event propagation to stop the settings panel from closing
  const handleToggleClick = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  return (
    <>
      <ToggleButton onClick={handleToggleClick}>
        {label}
      </ToggleButton>
      <ExpandableContainer isExpanded={isExpanded}>
        {children}
      </ExpandableContainer>
    </>
  );
}