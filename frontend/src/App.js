import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import styled from 'styled-components';
import Map from './components/map/Map';
import Header from './components/Header';
import { createGlobalStyle } from 'styled-components';
import websitePalette from './styles/palette'; // Import your color palette

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
  return (
    <>
      <GlobalStyle /> {/* This applies global styles */}
      <Router>
        <AppContainer> {/* Use the styled component here */}
          {/* Navigation Links can go here */}
          <Header /> {/* Add the Header at the top */}
          <Routes>
            <Route path="/map" element={<Map />} />
          </Routes>
        </AppContainer>
      </Router>
    </>
  );
}

export default App;
