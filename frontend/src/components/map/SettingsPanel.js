import React, { useState } from 'react';
import styled from 'styled-components';
import websitePalette from '../../styles/palette';
import CustomCheckbox from './CustomCheckbox';
import ExpandableComponent from './ExpandableComponent';


const StyledSettingsPanel = styled.div`
  position: absolute;
  top: 0;
  right: ${({ $isOpen }) => $isOpen ? '0' : '-100%'};
  bottom: 0;
  width: clamp(300px, 15vw, 1200px);
  background-color: ${websitePalette.foreground};
  box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
  z-index: 1100;
  transition: right 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  border-radius: 40px 0 0 40px;
  overflow: hidden; // Important to contain the scrollable area

  // @media (max-width: 1000px) {
  //   width: 100vw;
  //   border-radius: 0px;
  //   right: ${({ $isOpen }) => $isOpen ? '0' : '-110vw'};
  // }
`;

const StyledScrollableForm = styled.form`
  flex: 1; // Takes all available space
  overflow-y: auto; // Makes it scrollable
`;

const StyledFormGroup = styled.div`
  margin: 0 auto;
  margin-top: clamp(0.5rem, 0.4vw, 2rem);
  margin-bottom: clamp(0.5rem, 0.4vw, 2rem);
  padding: clamp(1rem, 0.8vw, 4rem);
  border: clamp(0.15rem, 0.12vw, 1rem) solid black;
  border-radius: 40px;
  // @media (max-width: 1000px) { // for tablets
  //   border-radius: 0;
  // }

`;

const StyledButton = styled.button`
    background-color: ${websitePalette.secondary};
    color: ${websitePalette.text};
    margin: 0 auto; // Center the button
    margin-top: clamp(0.5rem, 0.4vw, 2rem);
    margin-bottom: clamp(0.5rem, 0.4vw, 2rem);
    border: clamp(0.15rem, 0.12vw, 1rem) solid black;
    font-size: clamp(1rem, 0.8vw, 4rem);
    font-weight: 600;
    padding: clamp(0.75rem, 0.6vw, 3rem) clamp(1.5rem, 1.2vw, 6rem);
    border-radius: 40px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    text-align: center;
    display: block; // Automatically takes full width, adjust as needed
    width: calc(100% - 4rem);


    @media (hover: hover) and (pointer: fine) {
        &:hover {
            background-color: #5b5ea6;
            color: ${websitePalette.accent};
            border: clamp(0.15rem, 0.12vw, 1rem) solid ${websitePalette.accent};
        }
    }
`;


export default function SettingsPanel({ onSettingsChange, availableAthletes, availableYears, $isOpen }) {
    const [selectedAthletes, setSelectedAthletes] = useState([]);
    const [selectedYears, setSelectedYears] = useState({});

    const handleYearChange = (year) => {
        setSelectedYears(prevYears => ({
            ...prevYears,
            [year]: !prevYears[year]
        }));
    };

    const handleAthleteChange = (athlete) => {
        setSelectedAthletes(prevSelection => {
            const athleteId = athlete.athlete_id.toString();
            if (prevSelection.some(a => a.id === athleteId)) {
                return prevSelection.filter(a => a.id !== athleteId);
            } else {
                return [...prevSelection, { id: athleteId, color: athlete.color }];
            }
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const years = Object.keys(selectedYears).filter(year => selectedYears[year]);
        const athleteIds = selectedAthletes.map(a => a.id);
        onSettingsChange({ years, selectedAthletes: athleteIds });
    };

    return (
        <StyledSettingsPanel $isOpen={$isOpen}>
            <StyledScrollableForm>
                <ExpandableComponent label="Years">
                    <StyledFormGroup>
                      {availableYears.length > 0 ? (
                                  availableYears.map((year) => (
                                      <CustomCheckbox
                                          key={year}
                                          id={year}
                                          checked={!!selectedYears[year]}
                                          onChange={() => handleYearChange(year)}
                                          label={year.toString()}
                                          color='#5b5ea6'
                                      />
                                  ))
                              ) : (
                                  <p>No years available</p>
                              )}
                    </StyledFormGroup>
                </ExpandableComponent>
                <ExpandableComponent label="Athletes">
                    <StyledFormGroup>
                      {availableAthletes.length > 0 ? (
                                  availableAthletes.map((athlete) => {
                                      const athleteId = athlete.athlete_id.toString();
                                      const isChecked = selectedAthletes.some(a => a.id === athleteId);
                                      return (
                                          <CustomCheckbox
                                              key={athleteId}
                                              id={athleteId}
                                              checked={isChecked}
                                              onChange={() => handleAthleteChange(athlete)}
                                              label={athlete.first_name}
                                              color={athlete.color}
                                          />
                                      );
                                  })
                              ) : (
                                  <p>No athletes available</p>
                              )}
                    </StyledFormGroup>
                </ExpandableComponent>
            </StyledScrollableForm>
            <StyledButton type="button" onClick={handleSubmit}>
                Update Map
            </StyledButton>
        </StyledSettingsPanel>
    );
};
