import React from 'react';
import styled, { keyframes, css } from 'styled-components';
import websitePalette from '../../styles/palette';

const CheckboxContainer = styled.label`
  display: flex;
  align-items: center;
  margin-bottom: clamp(1rem, 0.8vw, 4rem);
  margin-top: clamp(1rem, 0.8vw, 4rem);
  cursor: ${props => (props.disabled ? 'not-allowed' : 'pointer')};
  font-size: clamp(1rem, 0.8vw, 4rem);

  ${props =>
    props.disabled &&
    css`
      opacity: 0.6; // Grey out when disabled
    `}
`;

const visuallyHidden = `
  border: 0;
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
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
  width: clamp(1.3rem, 1.2vw, 4rem);
  height: clamp(1.3rem, 1.2vw, 4rem);
  margin-right: 0.625rem;
  box-sizing: border-box;
  border: clamp(0.15rem, 0.12vw, 1rem) solid ${websitePalette.accentForeground};
  background-color: ${props => (props.checked ? props.color : 'transparent')};
  border-radius: clamp(0.4rem, 0.35vw, 4rem);
  transition: opacity 0.3s, background-color 0.5s, box-shadow 0.3s;

  &:after {
    content: '';
    width: 100%;
    height: 100%;
    border-radius: inherit;
    background-color: ${props => (props.checked ? props.color : 'transparent')};
    opacity: ${props => (props.checked ? 1 : 0)};
  }

  @media (hover: hover) and (pointer: fine) {
    &:hover {
      box-shadow: ${props =>
        props.disabled ? 'none' : `0 0 0 3px ${props.color}`};
    }
  }

  ${InputCheckbox}:focus + & {
    animation: ${props =>
      props.disabled ? 'none' : css`${hapticCheckbox} 0.3s ease`};
  }

  ${props =>
    props.disabled &&
    css`
      background-color: ${websitePalette.disabledBackground};
      border-color: ${websitePalette.disabledForeground};
    `}
`;

const Label = styled.span`
  margin-left: clamp(0.5rem, 0.4vw, 2rem);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  max-width: calc(100% - 3.6rem);

  ${props =>
    props.disabled &&
    css`
      color: ${websitePalette.disabledText};
    `}
`;

export default function CustomCheckbox({
  id,
  checked,
  onChange,
  label,
  color,
  disabled = false,
}) {

  return (
    <CheckboxContainer disabled={disabled}>
      <InputCheckbox
        id={id}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        color={color}
        disabled={disabled}
      />
      <StyledCheckbox
        checked={checked}
        color={color}
        disabled={disabled}
      />
      <Label htmlFor={id} disabled={disabled}>
        {label}
      </Label>
    </CheckboxContainer>
  );
}
