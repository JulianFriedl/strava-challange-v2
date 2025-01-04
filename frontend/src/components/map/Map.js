import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MapDisplay from './MapDisplay';
import SettingsPanel from './SettingsPanel';
import styled, { keyframes, css } from 'styled-components';
import websitePalette from '../../styles/palette';
import { apiRequest } from '../../api';

const colors = [
  '#7209b7', // Deep Purple
  '#f72585', // Vibrant Pink
  '#4361ee', // Vivid Blue
  '#ff5400', // Bright Orange
  '#ff8900', // Orange-Yellow
  '#06d6a0', // Mint Green
  '#073b4c', // Dark Teal
  '#d00000', // Scarlet Red
  '#48cae4', // Light Cyan
  '#b5179e', // Magenta
  '#630146',
  '#002e07',
  '#3a0ca3', // Indigo
  '#0081a7',
  '#5e5d73',
];

const rotate = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(180deg);
  }
`;

const rotateBack = keyframes`
  from {
    transform: rotate(180deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const startupAnimation = keyframes`
  0% {
    transform: scale(0.8);
  }
  15% {
    transform: scale(1.05);
  }
  25% {
    transform: scale(0.96);
  }
  35% {
    transform: scale(1.03);
  }
  45% {
    transform: scale(0.97);
  }
  50% {
    transform: scale(1.02);
  }
  60% {
    transform: scale(0.98);
  }
  70% {
    transform: scale(1.01);
  }
  80% {
    transform: scale(0.99);
  }
  90% {
    transform: scale(1);
  }
  100% {
    transform: scale(1);
  }
`;

const MapContainer = styled.div`
  position: relative;
  height: calc(var(--vh, 1vh) * 80); /* Dynamically adjust to mobile viewport */
  width: 85vw;
  margin: auto;
  border-radius: 40px;
  overflow: hidden;

  @media (max-width: 1000px) {
    width: 100vw;
  }
`;

const SettingsButton = styled.button`
  position: absolute;
  top: 30px;
  right: ${({ $isOpen }) => $isOpen ? `clamp(260px, 16vw, 1210px)` : `clamp(10px, 1vw, 40px)`};
  z-index: 1200;
  background-color: ${({ $isOpen }) => $isOpen ? '#5b5ea6' : websitePalette.secondary};
  color: ${({ $isOpen }) => $isOpen ? websitePalette.accent : websitePalette.text};
  border: ${({ $isOpen }) => $isOpen ? 'clamp(0.15rem, 0.12vw, 1rem) solid ' + websitePalette.accent : 'clamp(0.15rem, 0.12vw, 1rem) solid black'};
  border-radius: 50%;
  width: clamp(3rem, 2.4vw, 12rem);
  height: clamp(3rem, 2.4vw, 12rem);
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: clamp(1.4rem, 1.2vw, 4rem);
  transition: all 0.3s ease-in-out;

  @media (hover: hover) and (pointer: fine) {

    &:hover {
      background-color: ${({ $isOpen }) => $isOpen ? websitePalette.secondary : '#5b5ea6'};
      color: ${({ $isOpen }) => $isOpen ? websitePalette.text : websitePalette.accent};
      border: ${({ $isOpen }) => $isOpen ? '2px solid black' : '2px solid'+ websitePalette.accent};
    }
  }

  ${({ $isFirstRender, $isOpen, $hasInteracted }) => {
    if ($isFirstRender) {
      return css`animation: ${startupAnimation} 1.2s ease-out forwards;`;
    } else if ($hasInteracted) {
      return $isOpen ? css`animation: ${rotate} 0.3s linear forwards;` : css`animation: ${rotateBack} 0.3s linear forwards;`;
    }
  }}
`;

const Map = ({ authState }) => {
  const [years, setYears] = useState([]);
  const [selectedAthletes, setSelectedAthletes] = useState([]);
  const [availableAthletes, setAvailableAthletes] = useState([]);
  const [availableYears, setAvailableYears] = useState([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isFirstRender, setIsFirstRender] = useState(true);
  const [hasInteracted, setHasInteracted] = useState(false);
  const [isLoading, setIsLoading] = useState(false); // New state for loading

  const navigate = useNavigate();

useEffect(() => {
  if (authState && !authState.loggedIn) {
    navigate('/');
  }
}, [authState, navigate]);

useEffect(() => {
    // Fetch available athletes
    apiRequest('/map/athletes')
        .then((data) => {
            const athletesWithColors = data.map((athlete, index) => {
                const color = colors[index % colors.length];
                return { ...athlete, color };
            });
            setAvailableAthletes(athletesWithColors);
        })
        .catch((error) => {
            console.error('Error fetching athletes:', error);
            setAvailableAthletes([]); // Provide an empty state
        });

    // Fetch available years
    apiRequest('/map/years')
        .then((data) => setAvailableYears(data))
        .catch((error) => {
            console.error('Error fetching years:', error);
            setAvailableYears([]); // Provide an empty state
        });

    const timer = setTimeout(() => setIsFirstRender(false), 1200);
    return () => clearTimeout(timer);
}, []);

  const handleSettingsChange = (settings) => {
      if (isLoading) return

      const yearsChanged = JSON.stringify(settings.years) !== JSON.stringify(years);

      const athletesChanged = JSON.stringify(settings.selectedAthletes.map(String).sort()) !==
          JSON.stringify(selectedAthletes.map((athlete) => String(athlete.athlete_id)).sort());

      if (!yearsChanged && !athletesChanged) {
          // console.log("No changes detected in settings, skipping update.");
          return;
      }
      setIsLoading(true);

      // Update states with new settings
      setYears(settings.years);

      const selectedAthleteDetails = settings.selectedAthletes.map((id) =>
          availableAthletes.find((athlete) => athlete.athlete_id.toString() === id)
      );
      setSelectedAthletes(selectedAthleteDetails);
  };

  const handleMapLoadComplete = React.useCallback(() => {
    setIsLoading(false);
  }, []);

  const toggleSettings = () => {
    setIsSettingsOpen(!isSettingsOpen);
    if (!hasInteracted) setHasInteracted(true)
  };

  return (
    <MapContainer>
      <MapDisplay years={years} selectedAthletes={selectedAthletes} isLoading={isLoading} onLoadComplete={handleMapLoadComplete}/>
      <SettingsButton $isOpen={isSettingsOpen} $isFirstRender={isFirstRender} $hasInteracted={hasInteracted} onClick={toggleSettings}>
        {'<'}
      </SettingsButton>
      <SettingsPanel
        onSettingsChange={handleSettingsChange}
        availableAthletes={availableAthletes}
        availableYears={availableYears}
        $isOpen={isSettingsOpen}
      />
  </MapContainer>
  );
}

export default Map;
