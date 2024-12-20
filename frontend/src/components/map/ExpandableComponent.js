import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import websitePalette from '../../styles/palette';

// Animation for expanding/collapsing
const expandAnimation = keyframes`
  from {
    max-height: 0;
    opacity: 0;
  }
  to {
    100vh
    opacity: 1;
  }
`;

const collapseAnimation = keyframes`
  from {
    100vh
    opacity: 1;
  }
  to {
    max-height: 0;
    opacity: 0;
  }
`;

const ExpandableContainer = styled.div`
  overflow: hidden;
  animation: ${({ isExpanded }) => (isExpanded ? expandAnimation : collapseAnimation)} 0.5s ease forwards;
  background: ${websitePalette.backgroundLight};
  border-radius: 40px;
`;

const ToggleButton = styled.button`
  display: flex;
  margin: 0 auto; // Center the button
  margin-top: clamp(0.5rem, 0.4vw, 2rem);
  margin-bottom: clamp(0.5rem, 0.4vw, 2rem);
  align-items: center;
  justify-content: space-between;
  background: ${websitePalette.secondary};
  color: ${websitePalette.text};
  border: clamp(0.15rem, 0.12vw, 1rem) solid black;
  cursor: pointer;
  padding: clamp(0.75rem, 0.6vw, 3rem) clamp(1.5rem, 1.2vw, 6rem);
  font-size: clamp(1rem, 0.8vw, 4rem);
  font-weight: 600;
  width: calc(100% - 4rem);
  border-radius: 40px;
  transition: background-color 0.3s ease, transform 0.3s ease;

  @media (hover: hover) and (pointer: fine) {
    &:hover {
      background-color: #5b5ea6;
      border: clamp(0.15rem, 0.12vw, 1rem) solid ${websitePalette.accent};
      color: ${websitePalette.accent};
    }
  }

`;

const ArrowIcon = styled.span`
  display: inline-block;
  margin-left: clamp(1rem, 0.8vw, 4rem);
  font-size: clamp(1rem, 0.8vw, 4rem);
  transform: ${({ isExpanded }) => (isExpanded ? 'rotate(90deg)' : 'rotate(0deg)')};
  transition: transform 0.3s ease;
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
      <ToggleButton onClick={handleToggleClick} aria-expanded={isExpanded}>
        <span>{label}</span>
        <ArrowIcon isExpanded={isExpanded}>▶</ArrowIcon>
      </ToggleButton>
      <ExpandableContainer isExpanded={isExpanded}>
        {children}
      </ExpandableContainer>
    </>
  );
}
