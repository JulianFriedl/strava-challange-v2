import React, { useState } from 'react';
import styled from 'styled-components';

const Container = styled.div`
  max-width: min(1200px, 90vw);
  margin: 0 auto;
  padding: clamp(12px, 2vw, 24px);
`;

const Card = styled.div`
  padding: clamp(16px, 3vw, 24px);
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background-color: white;
`;

const LeaderboardCard = styled(Card)`
  width: 100%;
  max-width: min(600px, 90vw);
  margin: 0 auto clamp(16px, 4vw, 32px) auto;
`;

const SportCategoryCard = styled(Card)`
  width: clamp(280px, 45vw, 400px);
  flex-shrink: 0;

  @media (max-width: 768px) {
    width: min(400px, 90vw);
  }
`;

const Header = styled.h2`
  margin: 0 0 clamp(12px, 2vw, 20px) 0;
  font-size: clamp(18px, 2.5vw, 24px);
  font-weight: bold;
  text-align: center;
`;

const List = styled.div`
  height: clamp(200px, 40vh, 400px);
  overflow-y: auto;
  padding: 0 clamp(12px, 2vw, 20px);

  /* Scrollbar styling */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }
`;

const ListItem = styled.div`
  display: flex;
  justify-content: space-between;
  padding: clamp(4px, 1vw, 8px) 0;
`;

const NameContainer = styled.div`
  display: flex;
  gap: clamp(6px, 1vw, 10px);
`;

const Ranking = styled.span`
  min-width: 20px;
`;

const Name = styled.span`
  font-weight: 500;
`;

const Points = styled.span`
  margin-left: clamp(6px, 1vw, 10px);
`;

const SwipeContainer = styled.div`
  position: relative;
  overflow: hidden;
  margin: clamp(16px, 3vw, 32px) 0;
`;

const SwipeWrapper = styled.div`
  display: flex;
  gap: clamp(16px, 3vw, 32px);
  justify-content: center;
  flex-wrap: wrap;

  @media (min-width: 769px) {
    flex-wrap: nowrap;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: clamp(12px, 2vw, 20px);
  margin-top: clamp(12px, 2vw, 20px);
`;

const Button = styled.button`
  padding: clamp(8px, 1.5vw, 12px) clamp(12px, 2vw, 20px);
  border: none;
  border-radius: 6px;
  background-color: #3B82F6;
  color: white;
  cursor: pointer;
  font-size: clamp(14px, 1.5vw, 16px);
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #2563EB;
  }

  &:disabled {
    background-color: #D1D5DB;
    cursor: not-allowed;
  }
`;

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
  const isMobile = window.innerWidth <= 768;
  const cardsToShow = isMobile ? 1 : 2;

  const handleNext = () => {
    if (currentStartIndex < categories.length - cardsToShow) {
      setCurrentStartIndex(currentStartIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentStartIndex > 0) {
      setCurrentStartIndex(currentStartIndex - 1);
    }
  };

  const visibleCategories = categories.slice(
    currentStartIndex,
    currentStartIndex + cardsToShow
  );

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
          disabled={currentStartIndex >= categories.length - cardsToShow}
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