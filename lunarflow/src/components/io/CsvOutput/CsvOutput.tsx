// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React, { useState } from 'react';
import { Table } from 'antd';
import Papa from 'papaparse';
import CSVDownloader from './CsvDownloader';
import ReactMarkdown from 'react-markdown'

interface Props {
  csvString: string
}

const CSVOutput: React.FC<Props> = ({ csvString }) => {
  const [tableData, setTableData] = useState<any[]>([]);

  React.useEffect(() => {
    const parsedData = Papa.parse(csvString, { header: true }).data;
    setTableData(parsedData);
  }, [csvString]);

  const columns = tableData.length > 0 ? Object.keys(tableData[0]).map(key => ({
    title: key,
    dataIndex: key,
    render: (value: any) => {
      if (typeof value === 'string') {
        return <ReactMarkdown>{value}</ReactMarkdown>
      }
      return value;
    }
  })) : [];

  return (<div style={{ display: 'flex', flexDirection: 'column' }}>
    <Table dataSource={tableData} columns={columns} pagination={false} />
    <CSVDownloader csvString={csvString} />
  </div>
  );
};

export default CSVOutput;