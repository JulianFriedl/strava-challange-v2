import React from 'react';
import { Route, Routes, Link } from 'react-router-dom'; // Use Routes and element
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Chart1 from './Chart1.js';
import Chart2 from './Chart2';
import Chart3 from './Chart3';

const AnalyticsContainer = styled.div`
  display: flex;
  height: 100%;
`;

const Sidebar = styled.div`
  width: 200px;
  background-color: #f4f4f4;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
`;

const SidebarTitle = styled.h3`
  margin-top: 0;
`;

const SidebarList = styled.ul`
  list-style-type: none;
  padding: 0;
`;

const SidebarItem = styled.li`
  margin-bottom: 10px;
`;

const SidebarLink = styled(Link)`
  text-decoration: none;
  color: #333;
  font-size: 16px;
  
  &:hover {
    color: #007bff;
  }
`;

const ChartArea = styled.div`
  flex-grow: 1;
  padding: 20px;
  background-color: #fff;
  border-left: 1px solid #ddd;
`;

const  AnalyticsPage = ({authState}) => {
    const navigate = useNavigate();

useEffect(() => {
  if (authState && !authState.loggedIn) {
    navigate('/');
  }
}, [authState, navigate]);
  return (
    <AnalyticsContainer>
      <Sidebar>
        <SidebarTitle>Charts</SidebarTitle>
        <SidebarList>
          <SidebarItem><SidebarLink to="/analytics/chart1">Chart 1</SidebarLink></SidebarItem>
          <SidebarItem><SidebarLink to="/analytics/chart2">Chart 2</SidebarLink></SidebarItem>
          <SidebarItem><SidebarLink to="/analytics/chart3">Chart 3</SidebarLink></SidebarItem>
        </SidebarList>
      </Sidebar>
      <ChartArea>
        <Routes>
          <Route path="/analytics/chart1" element={<Chart1 />} />
          <Route path="/analytics/chart2" element={<Chart2 />} />
          <Route path="/analytics/chart3" element={<Chart3 />} />
          <Route path="/analytics" element={<Chart1 />} /> {/* Default chart */}
        </Routes>
      </ChartArea>
    </AnalyticsContainer>
  );
}

export default AnalyticsPage;