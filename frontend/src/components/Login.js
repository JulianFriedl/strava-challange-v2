import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import StravaButton from './StravaButton';
import websitePalette from '../styles/palette';
import About from './About';
import RankingTab from './ranking/Leaderboard.js';
import { apiRequest } from '../api.js';

const LoginContainer = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
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

const ErrorMessage = styled.p`
  color: red;
  margin: 20px 0;
`;

const LoadingMessage = styled.p`
  color: ${websitePalette.secondary};
  margin: 20px 0;
`;

const Login = ({ authState }) => {
  const [sportCategories, setSportCategories] = useState([]);
  const [overallRankings, setOverallRankings] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLeaderboardData = async () => {
      if (!authState.loggedIn) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        const data = await apiRequest('/leaderboard');
        
        // Separate and transform the categories
        const transformedCategories = data.leaderboard.map(category => {
          // Transform the rankings
          const transformedRankings = category.rankings.map(ranking => ({
            ...ranking,
            points: category.name === 'Overall'
              ? ranking.points
              : category.name === 'Alpine Snow Sports'
                ? `${ranking.points}m`
                : `${(ranking.points / 60)}h`
          }));

          // Return the transformed category
          return {
            ...category,
            rankings: transformedRankings
          };
        });

        // Find and set the Overall category
        const overallCategory = transformedCategories.find(category => 
          category.name === 'Overall'
        );
        if (overallCategory) {
          setOverallRankings(overallCategory);
        }

        // Set all categories
        setSportCategories(transformedCategories);
      } catch (error) {
        console.error('Error fetching categories:', error);
        setError('Failed to load leaderboard data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaderboardData();
  }, [authState.loggedIn]); // Only re-run if login status changes

  // Render login screen for non-authenticated users
  if (!authState.loggedIn) {
    return (
      <LoginContainer>
        <Title>Welcome</Title>
        <Description>Log in to explore your routes, stats, and more!</Description>
        <About />
      </LoginContainer>
    );
  }

  // Render loading state while keeping the container and title visible
  return (
    <LoginContainer>
      <Title>Leaderboards!</Title>
      {isLoading && (
        <LoadingMessage>Loading leaderboard data...</LoadingMessage>
      )}
      {error && (
        <ErrorMessage>{error}</ErrorMessage>
      )}
      {!isLoading && !error && sportCategories && sportCategories.length > 0 && (
        <RankingTab 
          sportCategories={sportCategories}
          overallRankings={overallRankings}
        />
      )}
      {!isLoading && !error && (!sportCategories || sportCategories.length === 0) && (
        <Description>No leaderboard data available.</Description>
      )}
    </LoginContainer>
  );
};

export default Login;