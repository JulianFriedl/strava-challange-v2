import React, { useEffect, useRef } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Register the necessary components for Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Chart1 = () => {
  const chartRef = useRef(null); // Reference to the canvas element

  useEffect(() => {
    if (!chartRef.current) return; // Ensure the canvas is available

    const ctx = chartRef.current.getContext('2d'); // Get the 2D context for drawing on the canvas

    // Check if the context is valid
    if (ctx) {
      new ChartJS(ctx, {
        type: 'line', // Type of chart (line chart)
        data: {
          labels: ['January', 'February', 'March', 'April', 'May'], // X-axis labels
          datasets: [
            {
              label: 'My First Dataset', // Dataset label
              data: [65, 59, 80, 81, 56], // Y-axis data
              borderColor: 'rgb(75, 192, 192)', // Line color
              backgroundColor: 'rgba(75, 192, 192, 0.2)', // Area under the line color
              fill: true, // Fill the area below the line
              tension: 0.4, // Smooth the line
            },
          ],
        },
        options: {
          responsive: true, // Make the chart responsive
          plugins: {
            title: {
              display: true,
              text: 'My Line Chart', // Title of the chart
            },
          },
        },
      });
    }
  }, []);

  return (
    <div>
      <h2>Line Chart Example</h2>
      {/* Ensure canvas has fixed dimensions */}
      <canvas ref={chartRef} width="400" height="200" />
    </div>
  );
};

export default Chart1;