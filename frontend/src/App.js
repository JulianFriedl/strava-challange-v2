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
import About from './components/About.js';
import Analytics from './components/analytics/Analytics.js'

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
  #root {
    height: 100%;
  }

  .full-height {
    height: calc(var(--vh, 1vh) * 100); /* Use custom viewport height */
  }

  input[type="checkbox"], input[type="radio"] {
    -webkit-appearance: none; /* Remove default iOS styles */
    appearance: none; /* Normalize across browsers */
    margin: 0; /* Reset margin for consistent alignment */
  }

  input[type="checkbox"] {
    position: relative; /* Ensure proper stacking context */
    z-index: -1; /* Ensure it doesn’t interfere with visible styles */
  }

  label, span, button {
    touch-action: manipulation; /* Improve touch behavior on mobile */
  }

`;

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: calc(var(--vh, 1vh) * 100);
`;

function App() {
  const [authState, setAuthState] = useState({ loggedIn: false, userId: null });
  const [isLoading, setIsLoading] = useState(true);
  useEffect(() => {
      // Adjust the viewport height for mobile browsers
      const setViewportHeight = () => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
      };

      setViewportHeight(); // Set on initial load
      window.addEventListener('resize', setViewportHeight); // Update on resize

      return () => {
        window.removeEventListener('resize', setViewportHeight);
      };
    }, []);
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
            <Route path="/" element={<Login authState={authState} />} />
            <Route path="/map" element={<Map authState={authState} />} />
            <Route path="/about" element={<About />} />
            <Route path="/analytics/*" element={<Analytics authState={authState}/>}/>
          </Routes>
          <Overlay />
        </AppContainer>
      </Router>
    </>
  );
}

export default App;
