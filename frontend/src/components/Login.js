import React from 'react';
import styled from 'styled-components';
import StravaButton from './StravaButton';
import websitePalette from '../styles/palette';
import About from './About';

const LoginContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center; align-items: center;
  background-color: ${websitePalette.background};
  color: ${websitePalette.text};
  text-align: center;
  padding: 20px;
`;

const Title = styled.h1`
  font-size: clamp(2rem, 3vw, 40rem);
  margin-bottom: 20px;
  color: ${websitePalette.primary};
`;

const Description = styled.p`
  font-size: clamp(1rem, 1vw, 10rem);
  margin-bottom: 40px;
  color: ${websitePalette.secondary};
`;

const StravaButtonWrapper = styled.div`
  display: inline-block;
`;

const LoggedInMessage = styled.p`
  font-size: clamp(1rem, 1vw, 10rem);
  color: ${websitePalette.accent};
`;

const Login = ({ authState }) => {
  if (authState.loggedIn) {
    return (
      <LoginContainer>
        <Title>Welcome Back!</Title>
        <LoggedInMessage>
          You are logged in as User {authState.userId}. Go to the <a href="/map">map</a> to explore your routes.
        </LoggedInMessage>
      </LoginContainer>
    );
  }

  return (
    <LoginContainer>
      <Title>Welcome</Title>
      <Description>Log in to explore your routes, stats, and more!</Description>
      {/* <StravaButtonWrapper>
        <StravaButton />
      </StravaButtonWrapper> */}
      <About />
    </LoginContainer>
  );
};

export default Login;
