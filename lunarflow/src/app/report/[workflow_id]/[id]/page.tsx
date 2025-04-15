// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import React from 'react';
import { Layout } from 'antd';
import Tiptap from '@/components/report/TipTap';
import { redirect } from 'next/navigation';
import { createReportAction, getReportAction } from '@/app/actions/report';
import { getUserId } from '@/utils/getUserId';

export default async function Home({ params }: { params: { workflow_id: string, id: string } }) {
  const userId = await getUserId()

  const saveReport = async (htmlString: string, reportName: string) => {
    "use server"
    if (userId) {
      await createReportAction(reportName, htmlString, params.workflow_id, userId)
    } else {
      redirect('/login')
    }
  }

  const report = await getReportAction(params.workflow_id, params.id, userId)

  return <Layout style={{ height: '100%', backgroundColor: '#fff', overflow: 'scroll' }}>
    <Layout style={{ backgroundColor: '#fff' }}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        maxWidth: 800,
        width: '100%',
        flexGrow: 1,
        marginRight: 'auto',
        marginLeft: 'auto',
        minHeight: '100vh',
      }}
      >
        <Tiptap report={report} saveReport={saveReport} />
        {/* <Report workflowId={params.workflow_id} reportId={params.id} /> */}
      </div>
    </Layout>
  </Layout>
}