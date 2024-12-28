import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import styled from 'styled-components';
import Map from './components/map/Map';
import Login from './components/Login.js'
import Header from './components/Header';
import Overlay from './components/Overlay';
import { createGlobalStyle } from 'styled-components';
import websitePalette from './styles/palette';
import { API_BASE_URL } from './api';

export const GlobalStyle = createGlobalStyle`
  *,
  *::before,
  *::after {
    box-sizing: border-box;
  }

  body {
    background-color: ${websitePalette.background};
    color: ${websitePalette.text};
    font-family: 'Arial', sans-serif;
  }
`;

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
`;

function App() {
  const [authState, setAuthState] = useState({ loggedIn: false, userId: null });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAuthState = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/status`, {
          credentials: 'include',
        });
        if (response.ok) {
          const data = await response.json();
          setAuthState({ loggedIn: data.logged_in, userId: data.user_id });
        } else {
          setAuthState({ loggedIn: false, userId: null });
        }
      } catch (error) {
        console.error('Error fetching auth state:', error);
        setAuthState({ loggedIn: false, userId: null });
      } finally {
        setIsLoading(false);
      }
    };

    fetchAuthState();
  }, []);

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      setAuthState({ loggedIn: false, userId: null });
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <GlobalStyle />
      <Router>
        <AppContainer>
          <Header authState={authState} onLogout={handleLogout} />
          <Routes>
            <Route path="/map" element={<Map authState={authState} />} />
            <Route path="/" element={<Login authState={authState} />} />
          </Routes>
          <Overlay />
        </AppContainer>
      </Router>
    </>
  );
}

export default App;
