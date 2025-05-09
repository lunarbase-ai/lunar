// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { BarElement, Chart } from "chart.js";
import { Bar } from 'react-chartjs-2';
import { Space } from "antd"
import { ChartData } from 'chart.js';

Chart.register(
  BarElement
);

interface BarChartOutputProps {
  data: {
    data: Record<string, number>,
    images: string[]
  }
}

const BarChartOutput: React.FC<BarChartOutputProps> = ({ data }) => {
  const plotData = data.data
  const chartData: ChartData<'bar'> = {
    labels: Object.keys(plotData),
    datasets: [{
      data: Object.values(plotData),
      backgroundColor: 'rgb(30, 50, 87)'
    }]
  }
  return <Space direction="vertical" style={{ width: '100%', maxHeight: 100 }}>
    <Bar
      width='100%'
      height={50}
      data={chartData}
    />
  </Space>
}

export default BarChartOutput
