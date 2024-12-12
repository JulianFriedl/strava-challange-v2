import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import websitePalette from '../../styles/palette';

const CheckboxContainer = styled.label`
  display: flex;
  align-items: center;
  margin-bottom: 1rem; // Using rem for consistent scaling
  cursor: pointer;
  font-size: 1rem; // Base font size for better accessibility

  @media (max-width: 1000px) { 
    font-size: 1.5rem; 
  }
`;

const visuallyHidden = `
  border: 0;
  clip: rect(0 0 0 0);
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
  position: absolute;
  width: 1px;
  white-space: nowrap;
`;

const InputCheckbox = styled.input.attrs({ type: 'checkbox' })`
  ${visuallyHidden}
`;

const hapticCheckbox = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
`;

const StyledCheckbox = styled.span`
  width: 1.5rem; 
  height: 1.5rem;

  @media (max-width: 1000px) {
    width: 2.5rem; 
    height: 2.5rem;
  }

  margin-right: 0.625rem; 
  box-sizing: border-box;
  border: 2px solid #ccc;
  background-color: ${props => props.checked ? props.color : 'transparent'};
  border-radius: 0.3125rem; 
  justify-content: center;
  align-items: center;
  transition: opacity 0.3s, background-color 0.5s, box-shadow 0.3s;

  &:after {
    content: '';
    width: 100%;
    height: 100%;
    border-radius: inherit;
    background-color: ${props => props.checked ? props.color : 'transparent'};
    opacity: ${props => props.checked ? 1 : 0};
  }

  // Hover effect
  @media (hover: hover) and (pointer: fine) {
    &:hover {
      box-shadow: 0 0 0 3px ${props => props.color}; 
    }
  }

  ${InputCheckbox}:focus + &{
    animation: ${hapticCheckbox} 0.3s ease;
  }
`;

const Label = styled.span`
  margin-left: 0.5rem; // Converted to rem
  overflow: hidden; // Hide overflowed content
  white-space: nowrap; // Prevent text from wrapping to a new line
  text-overflow: ellipsis; // Add ellipsis to overflowed content
  max-width: calc(100% - 3.6rem); // Adjust max-width as necessary, considering the size of the checkbox and margins
`;

export default function CustomCheckbox({ id, checked, onChange, label, color }) {
    return (
        <CheckboxContainer>
            <InputCheckbox
                id={id}
                type="checkbox"
                checked={checked}
                onChange={onChange}
                color={color}
            />
            <StyledCheckbox
                checked={checked}
                color={color} />
            <Label htmlFor={id}>{label}</Label>
        </CheckboxContainer>
    );
}