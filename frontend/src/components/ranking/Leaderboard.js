import React, { useState } from 'react';
import styled from 'styled-components';
import websitePalette from '../../styles/palette';
import { apiRequest } from '../../api';

const Card = styled.div`
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background-color: white;
`;

const LeaderboardCard = styled(Card)`
  width: 100%;
  max-width: 400px;
  margin: 0 auto 24px auto;
`;

const SportCategoryCard = styled(Card)`
  width: 400px;
  flex-shrink: 0;
`;

const Header = styled.h2`
  margin: 0 0 16px 0;
  font-size: 20px;
  font-weight: bold;
  text-align: center;
`;

const List = styled.div`
  height: 200px;
  overflow-y: auto;
  padding: 0 16px;
`;

const ListItem = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
`;

const NameContainer = styled.div`
  display: flex;
  gap: 8px;
`;

const Ranking = styled.span`
  min-width: 20px;
`;

const Name = styled.span`
  font-weight: 500;
`;

const Points = styled.span`
  margin-left: 8px;
`;

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
`;

const SwipeContainer = styled.div`
  position: relative;
  overflow: hidden;
  margin: 24px 0;
`;

const SwipeWrapper = styled.div`
  display: flex;
  gap: 24px;
  justify-content: center;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
`;

const Button = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #3B82F6;
  color: white;
  cursor: pointer;

  &:hover {
    background-color: #2563EB;
  }

  &:disabled {
    background-color: #D1D5DB;
    cursor: not-allowed;
  }
`;

// Updated Leaderboard component with safety checks
const Leaderboard = ({ rankings = [] }) => {
  if (!Array.isArray(rankings)) {
    console.error('Rankings prop must be an array');
    return null;
  }

  return (
    <LeaderboardCard>
      <Header>Overall Leaderboard</Header>
      <List>
        {rankings.map((rank, index) => (
          <ListItem key={index}>
            <NameContainer>
              <Ranking>{`${index + 1}.`}</Ranking>
              <Name>{rank.name}</Name>
            </NameContainer>
            <Points>{rank.points}</Points>
          </ListItem>
        ))}
      </List>
    </LeaderboardCard>
  );
};

const SportCard = ({ category, rankings }) => (
  <SportCategoryCard>
    <Header>{category}</Header>
    <List>
      {rankings.map((rank, index) => (
        <ListItem key={index}>
          <NameContainer>
            <Ranking>{`${index + 1}.`}</Ranking>
            <Name>{rank.name}</Name>
          </NameContainer>
          <Points>{rank.points}</Points>
        </ListItem>
      ))}
    </List>
  </SportCategoryCard>
);

const SwipeCards = ({ categories }) => {
  const [currentStartIndex, setCurrentStartIndex] = useState(0);

  const handleNext = () => {
    if (currentStartIndex < categories.length - 2) {
      setCurrentStartIndex(currentStartIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentStartIndex > 0) {
      setCurrentStartIndex(currentStartIndex - 1);
    }
  };

  const visibleCategories = categories.slice(currentStartIndex, currentStartIndex + 2);

  return (
    <div>
      <SwipeContainer>
        <SwipeWrapper>
          {visibleCategories.map((category, index) => (
            <SportCard 
              key={`${category.name}-${currentStartIndex + index}`}
              category={category.name}
              rankings={category.rankings}
            />
          ))}
        </SwipeWrapper>
      </SwipeContainer>

      <ButtonContainer>
        <Button 
          onClick={handlePrev} 
          disabled={currentStartIndex === 0}
        >
          Previous
        </Button>
        <Button 
          onClick={handleNext} 
          disabled={currentStartIndex >= categories.length - 2}
        >
          Next
        </Button>
      </ButtonContainer>
    </div>
  );
};

const RankingTab = ({ overallRankings, sportCategories }) => {
  const rankings = overallRankings?.rankings || [];
  const filteredCategories = sportCategories?.filter(cat => cat.name !== 'Overall') || [];

return (
    <Container>
      <Leaderboard rankings={rankings} />
      {filteredCategories.length > 0 && (
        <SwipeCards categories={filteredCategories} />
      )}
    </Container>
  );
};

export default RankingTab;