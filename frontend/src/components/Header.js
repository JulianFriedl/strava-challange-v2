import React from 'react';
import styled from 'styled-components';
import HomeButton from './HomeButton';
import StravaButton from './StravaButton';
import LogoutButton from './LogoutButton.js'
import websitePalette from '../styles/palette';
import {Link} from "react-router-dom";

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
    <header>
      <div>
        <HomeButton />
      </div>

      <div>
        {/* Add other navigation links if needed */}
        <StyledLink to ="/">Ranking</StyledLink>
        <StyledLink to ="/analytics">Analytics</StyledLink>
        <StyledLink to ="/map">Map</StyledLink>
        <StyledLink to ="/about">About/Rules</StyledLink>
      </div>

      <div>
        {authState.loggedIn ? (
          <LogoutButton onLogout={onLogout} />
        ) : (
          <StravaButton />
        )}
      </div>
    </header>
  );
};

export default Header;
