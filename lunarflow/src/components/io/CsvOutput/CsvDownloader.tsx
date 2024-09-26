// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Button } from 'antd';
import React from 'react';

interface CSVDownloaderProps {
  csvString: string;
}

class CSVDownloader extends React.Component<CSVDownloaderProps> {
  downloadCSV = () => {
    const { csvString } = this.props;
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'data.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  render() {
    return (
      <Button onClick={this.downloadCSV} style={{ width: '100%' }}>
        Download CSV
      </Button>
    );
  }
}

export default CSVDownloader;
