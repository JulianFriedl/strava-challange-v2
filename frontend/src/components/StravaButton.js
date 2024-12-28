import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { apiRequest } from '../api';

const ButtonContainer = styled.div`
  display: inline-block;
  cursor: pointer;
  width: clamp(12rem, 9.6vw, 48rem);

  img { width: 100%;
    height: 100%;
    object-fit: contain; /* Prevent distortion */
    vertical-align: middle; /* Fix extra spacing below the image */
    transition: transform 0.2s ease;

    &:hover {
      transform: scale(1.1);
    }
  }
`;

const StravaButton = () => {
  const [stravaAuthUrl, setStravaAuthUrl] = useState('');

  useEffect(() => {
    apiRequest('/auth/strava_auth_url')
      .then((data) => {
          if (data.auth_url) {
              setStravaAuthUrl(data.auth_url); // Set the auth URL if it exists
          } else {
              console.error('No URL returned in response:', data);
          }
      })
      .catch((error) => {
          console.error('Error fetching Strava auth URL:', error);
      });
  }, []);

  const handleClick = () => {
    if (stravaAuthUrl) {
      window.location.href = stravaAuthUrl;
    }
  };

  return (
    <ButtonContainer onClick={handleClick} aria-label="Connect with Strava">
      <img src="/btn_strava_connectwith_light.svg" alt="Connect with Strava" />
    </ButtonContainer>
  );
};

export default StravaButton;
