// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { CategoryScale, Chart, LineElement, LinearScale, PointElement } from "chart.js";
import { Line } from 'react-chartjs-2';
import { Space } from "antd"
import { ChartData } from 'chart.js';

Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
);

interface LineChartOutputProps {
  data: {
    data: Record<string, number>,
    images: string[]
  }
}

const LineChartOutput: React.FC<LineChartOutputProps> = ({ data }) => {
  const chartData: ChartData<'line'> = {
    labels: Object.keys(data.data),
    datasets: [{
      data: Object.values(data.data),
      borderColor: 'rgb(255, 99, 132)'
    }]
  }
  return <Space direction="vertical" style={{ width: '100%' }}>
    <Line width='100%' data={chartData} />
  </Space>
}

export default LineChartOutput
