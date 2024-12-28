import React from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import websitePalette from '../styles/palette';


const LogoContainer = styled.div`
  display: inline-block;
  cursor: pointer;
  width: clamp(3rem, 2.4vw, 12rem);
  height: clamp(3rem, 2.4vw, 12rem);

  img {
    width: 100%;
    height: 100%;
    transition: transform 0.2s ease;

    &:hover {
      transform: scale(1.1); /* Optional hover effect */
      fill: ${websitePalette.hoverAccent || '#9c9ede'};
    }
  }
`;

const HomeButton = () => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate('/');
  };

  return (
    <LogoContainer onClick={handleClick} aria-label="Return to Home">
      <img src="/logo.svg" alt="Home" />
    </LogoContainer>
  );
};

export default HomeButton;
