import React from 'react';
import styled from 'styled-components';

const OverlayContainer = styled.div`
  // position: fixed;
  bottom: 0; /* Or top: 0 for top placement */
  width: 100%;
  background-color: rgba(255, 255, 255, 0.5); /* Slight transparency */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 5px;
  // box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1); /* Optional shadow */
  z-index: 1000;
`;

const Overlay = () => (
  <OverlayContainer>
    <img
      src="/api_logo_pwrdBy_strava_horiz_gray.svg"
      alt="Powered by Strava"
      style={{ height: 'clamp(30px, 1.5vw, 200px)', objectFit: 'contain' }}
    />
  </OverlayContainer>
);

export default Overlay;
