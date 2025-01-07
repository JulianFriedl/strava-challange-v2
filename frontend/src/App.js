import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import styled from 'styled-components';
import Map from './components/map/Map';
import Login from './components/Login.js'
import StravaButton from './components/StravaButton.js';
import Header from './components/Header';
import { createGlobalStyle } from 'styled-components';
import websitePalette from './styles/palette';
import { API_BASE_URL } from './api';
import About from './components/About.js';
import Footer from './components/Footer.js';
import Analytics from './components/analytics/Analytics.js'
import './styles/layout.css'

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

`;

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
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

  if (!authState.loggedIn) {
    return (
      <>
      <GlobalStyle />
      <Router>
        <AppContainer>
          <Routes>
            <Route path="/" element={<Login authState={authState} />} />
            <Route path="/about" element={<About />} />
          </Routes>
          <div class="loginBtn">
            <StravaButton />
          </div>
          <Footer />
        </AppContainer>
      </Router>
    </>
    );
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
          <Footer />
        </AppContainer>
      </Router>
    </>
  );
}

export default App;
