import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import '../../styles/leaderboard.css'

const Container = styled.div`
  // border: 2px solid khaki;
  width: 80vw;
  display: flex;
  justify-content: space-evenly;
  align-items: start;
  height: 100vh;

  @media (max-width: 768px) {
    overflow-y: auto;
  }
`;

const Card = styled.div`
  border-radius: 25px;
  box-shadow: 0 0 10px #ccc;
  background-color: white;
  padding: 10px 30px 10px 30px;
`;

const LeaderboardCard = styled(Card)`
  height: 60%;
  width: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
`;

const SportCategoryCard = styled(Card)`
  flex-shrink: 0;
  width: 50%;
  overflow-y: auto;
  margin: 0 10px;

  @media (max-width: 768px) {
    width: min(400px, 90vw);
  }
`;

const Header = styled.h2`
  // margin: 0 0 clamp(12px, 2vw, 20px) 0;
  font-size: clamp(18px, 2.5vw, 24px);
  font-weight: bold;
  text-align: center;
`;

const List = styled.div`
  height: 100%;
  // height: clamp(200px, 40vh, 400px);
  // overflow-y: auto;
  // padding: 0 clamp(12px, 2vw, 20px);

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
  line-height: 30px;
`;

const NameContainer = styled.div`
  display: flex;
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
  // border: 2px solid red;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  height: 100%;
  width: 100%;
  padding: 20px 10px;
`;

const SwipeWrapper = styled.div`
  // border: 2px solid red;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  height: 100%;
  width: 90%;

  @media (min-width: 769px) {
    flex-wrap: nowrap;
  }
`;


const Leaderboard = ({ rankings = [] }) => {
  if (!Array.isArray(rankings)) {
    console.error('Rankings prop must be an array');
    return null;
  }

  return (
    <LeaderboardCard>
      <div class="innerCard">
        <Header>Overall Leaderboard</Header>
        <br />
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
      </div>
    </LeaderboardCard>
  );
};

const SportCard = ({ category, rankings }) => (
  <SportCategoryCard>
    <Header>{category}</Header>
    <br />
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
    <div class="rankings">
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
      <div class="buttons">
        <button
          onClick={handlePrev}
          disabled={currentStartIndex === 0}
        >
          Previous
        </button>
        <div class="space"/>
        <button
          onClick={handleNext}
          disabled={currentStartIndex >= categories.length - cardsToShow}
        >
          Next
        </button>
      </div>
    </div>
  );
};

const RankingTab = ({ overallRankings, sportCategories }) => {
  const rankings = overallRankings?.rankings || [];
  const filteredCategories = sportCategories?.filter(cat => cat.name !== 'Overall') || [];
  const [top3, setTop3] = useState([]);

  useEffect(() => {
    if (sportCategories) {
      let overall = sportCategories.filter(cat => cat.name === 'Overall')[0];
      setTop3(overall.rankings.slice(0, 3));
    }
  }, [sportCategories]);

  return (
    <Container>
      <div class="overall">
        <div class="top3">
          <div class="place">
            <img src={top3[1]?.url.full} alt={top3[1]?.name || ""} />
            <p>{top3[1]?.name || ""}</p>
            <div id="second" />
          </div>
          <div class="place">
            <img src={top3[0]?.url.full} alt={top3[0]?.name || ""} />
            <p>{top3[0]?.name || ""}</p>
            <div id="first" />
          </div>
          <div class="place">
            <img src={top3[2]?.url.full} alt={top3[2]?.name || ""} />
            <p>{top3[2]?.name || ""}</p>
            <div id="third" />
          </div>
        </div>
        <Leaderboard rankings={rankings} />
      </div>
      <hr id="leaderboard-hr"/>
      {filteredCategories.length > 0 && (
        <SwipeCards categories={filteredCategories} />
      )}
    </Container>
  );
};

export default RankingTab;
