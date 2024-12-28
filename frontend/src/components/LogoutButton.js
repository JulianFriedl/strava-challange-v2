import React from 'react';
import styled from 'styled-components';

const ButtonContainer = styled.div`
  display: inline-block;
  cursor: pointer;
  width: clamp(1.5rem, 1.5vw, 48rem);

  img {
    width: 100%;
    height: 100%;
    object-fit: contain; /* Prevent distortion */
    vertical-align: middle; /* Fix extra spacing below the image */
    transition: transform 0.2s ease;

    &:hover {
      transform: scale(1.1);
    }
  }
`;

const LogoutButton = ({ onLogout }) => {
  const handleClick = async () => {
    try {
      await onLogout();
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  return (
    <ButtonContainer onClick={handleClick} aria-label="Logout" role="button" tabIndex="0">
      <img src="/logout.svg" alt="logout" />
    </ButtonContainer>
  );
};

export default LogoutButton;
