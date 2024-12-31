import React from 'react';
import styled from 'styled-components';
import HomeButton from './HomeButton';
import StravaButton from './StravaButton';
import LogoutButton from './LogoutButton.js'
import websitePalette from '../styles/palette';
import {Link} from "react-router-dom";

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: ${websitePalette.background};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: clamp(4.5rem, 3.6vw, 50rem);
  z-index: 10;
  // position: fixed; /* Sticks to the top of the viewport */
  width: 100%;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

const CenterSection = styled.nav`
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

const StyledLink = styled(Link)`
  color: ${websitePalette.primary};
  text-decoration: none;
  font-weight: bold;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s, color 0.3s;

  &:hover {
    background-color: ${websitePalette.secondary};
    color: ${websitePalette.textOnSecondary};
  }
`;

const Header = ({ authState, onLogout }) => {
  return (
    <HeaderContainer>
      <LeftSection>
        <HomeButton />
      </LeftSection>

      <CenterSection>
        {/* Add other navigation links if needed */}
        <StyledLink to ="/">Ranking</StyledLink>
        <StyledLink to ="/analytics">Analytics</StyledLink>
        <StyledLink to ="/map">Map</StyledLink>
        <StyledLink to ="/about">About/Rules</StyledLink>
      </CenterSection>

      <RightSection>
        {authState.loggedIn ? (
          <LogoutButton onLogout={onLogout} />
        ) : (
          <StravaButton />
        )}
      </RightSection>
    </HeaderContainer>
  );
};

export default Header;
