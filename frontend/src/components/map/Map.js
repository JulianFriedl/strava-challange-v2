import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MapDisplay from './MapDisplay';
import SettingsPanel from './SettingsPanel';
import styled, { keyframes, css } from 'styled-components';
import websitePalette from '../../styles/palette';
import { apiRequest } from '../../api';
const colors = [
  '#f72585',
  '#7209b7',
  '#3a0ca3',
  '#4361ee',
  '#4cc9f0',
  '#ff5400',
  '#ff8900',
  '#affc41',
  '#b2ff9e'
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
  height: 80vh;
  width: 85vw;
  margin: auto;
  border-radius: 40px;
  overflow: hidden;

  // @media (max-width: 1000px) {
  //   margin: 0;
  //   height: 100vh;
  //   width: 100vw;
  //   border-radius: 0px;
  // }
`;

const SettingsButton = styled.button`
  position: absolute;
  top: 30px;
  right: ${({ $isOpen }) => $isOpen ? `clamp(320px, 16vw, 1210px)` : `clamp(10px, 1vw, 40px)`};
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
    setYears(settings.years);
    // Find the full athlete objects including their colors from selected IDs
    const selectedAthleteDetails = settings.selectedAthletes.map(id =>
      availableAthletes.find(athlete => athlete.athlete_id.toString() === id)
    );
    setSelectedAthletes(selectedAthleteDetails);
  };

  const toggleSettings = () => {
    setIsSettingsOpen(!isSettingsOpen);
    if (!hasInteracted) setHasInteracted(true)
  };

  return (
    <MapContainer>
      <MapDisplay years={years} selectedAthletes={selectedAthletes} />
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
