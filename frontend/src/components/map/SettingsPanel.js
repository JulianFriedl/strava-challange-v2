import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import websitePalette from '../../styles/palette';
import CustomCheckbox from './CustomCheckbox';
import ExpandableComponent from './ExpandableComponent';


const StyledSettingsPanel = styled.div`
  position: absolute;
  top: 0;
  right: ${({ isOpen }) => isOpen ? '0' : '-100%'};
  bottom: 0;
  width: 300px;
  background-color: ${websitePalette.foreground};
  box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
  z-index: 1100;
  transition: right 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  border-radius: 40px 0 0 40px;
  overflow: hidden; // Important to contain the scrollable area

  @media (max-width: 1000px) {
    width: 100vw;
    border-radius: 0px;
    right: ${({ isOpen }) => isOpen ? '0' : '-110vw'};
  }
`;

const StyledScrollableForm = styled.form`
  flex: 1; // Takes all available space
  overflow-y: auto; // Makes it scrollable
`;

const StyledFormGroup = styled.div`
  margin: 0 auto;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 1rem;
  border: 2px solid black;
  border-radius: 40px;
  @media (max-width: 1000px) { // for tablets
    border-radius: 0;
  }

`;

const StyledSectionHeader = styled.h2`
  font-weight: 600;
  color: #333;
  margin-top: 0.5rem;
`;
const StyledButton = styled.button`
    background-color: ${websitePalette.secondary};
    color: ${websitePalette.text};
    margin: 0 auto; // Center the button
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
    border: 2px solid black;
    font-size: 1rem;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    border-radius: 40px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    text-align: center;
    display: block; // Automatically takes full width, adjust as needed
    width: calc(100% - 4rem); // Adjust width as needed, considering the padding of the parent
    max-width: 20rem;


    @media (hover: hover) and (pointer: fine) {
        &:hover {
            background-color: #5b5ea6;
            color: ${websitePalette.accent};
            border: 2px solid ${websitePalette.accent};
        }
    }
`;


export default function SettingsPanel({ onSettingsChange, availableAthletes, availableYears, isOpen }) {
    const [selectedAthletes, setSelectedAthletes] = useState([]);
    const [selectedYears, setSelectedYears] = useState({});

    const handleYearChange = (year) => {
        setSelectedYears(prevYears => ({
            ...prevYears,
            [year]: !prevYears[year]
        }));
    };

    function handleAthleteChange(athlete) {
        setSelectedAthletes(prevSelection => {
            const athleteId = athlete.athlete_id.toString();
            if (prevSelection.some(a => a.id === athleteId)) {
                return prevSelection.filter(a => a.id !== athleteId);
            } else {
                return [...prevSelection, { id: athleteId, color: athlete.color }];
            }
        });
    };

    function handleSubmit(e) {
        e.preventDefault();
        const years = Object.keys(selectedYears).filter(year => selectedYears[year]);
        const athleteIds = selectedAthletes.map(a => a.id);
        // console.log(athleteIds);
        onSettingsChange({ years, selectedAthletes: athleteIds });
    };

    return (
        <StyledSettingsPanel isOpen={isOpen}>
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
