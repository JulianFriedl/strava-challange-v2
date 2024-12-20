import React from 'react';
import styled from 'styled-components';
import HomeButton from './HomeButton'; // Import the HomeButton component
import websitePalette from '../styles/palette'; // Import your color palette

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  padding: 10px 20px;
  background-color: ${websitePalette.background};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Optional shadow */
`;

const Header = () => {
  return (
    <HeaderContainer>
      <HomeButton />
      {/* Add other header elements */}
    </HeaderContainer>
  );
};

export default Header;
