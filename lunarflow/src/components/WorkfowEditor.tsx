// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

'use client'
import { Layout } from 'antd';
import { ReactFlowProvider } from 'reactflow';
import Image from 'next/image';
import { Session } from 'next-auth';
import 'reactflow/dist/style.css';
import Logo from '@/assets/Brand.png';

import Sidebar from '@/components/Sidebar';
import Workspace from '@/components/workspace/Workspace';
import WorkflowActions from '@/components/WorkflowActions';
import WorkflowEditorProvider from '@/contexts/WorkflowEditorContext';
import HeaderInput from '@/components/HeaderInput';
import { ComponentModel } from '@/models/component/ComponentModel';
import { Workflow } from '@/models/Workflow';
import AvatarDropdown from './AvatarDropdown';
import { SessionProvider } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import WorkflowRunningProvider from '@/contexts/WorkflowRunningContext';
import Sider from 'antd/es/layout/Sider';
import { useState } from 'react';
import EditorGenerateInput from './editorGenerateInput';

const { Content, Header } = Layout

interface WorkflowEditorProps {
  workflowId: string
  workflow: Workflow
  components: ComponentModel[]
  session: Session
}

const WorkflowEditor: React.FC<WorkflowEditorProps> = ({ workflowId, workflow, components, session }) => {
  const { push } = useRouter()
  const [collapsed, setCollapsed] = useState(false);

  return <WorkflowEditorProvider initialComponents={components}>
    <SessionProvider>
      <Layout style={{ height: '100%' }}>
        <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Image
            src={Logo}
            width={125}
            height={32}
            alt='Lunar'
            style={{ verticalAlign: 'middle', cursor: 'pointer' }}
            onClick={() => push('/')}
          />
          <HeaderInput />
          <AvatarDropdown session={session} />
        </Header>
        <Layout>
          <WorkflowRunningProvider>
            <ReactFlowProvider>
              <Sidebar />
              <Content
                style={{
                  margin: 0,
                  minHeight: 280,
                  background: '#fff',
                  position: 'relative',
                }}
              >
                <Workspace workflow={workflow} />
                <WorkflowActions workflowId={workflowId} isCollapsed={collapsed} toggleCollapsed={() => setCollapsed(prev => !prev)} />
              </Content>
              <Sider collapsed={collapsed} collapsedWidth={0} collapsible width={280} style={{ background: '#fff' }}>
                <div style={{ display: 'flex', height: '100%', width: '100%', flexDirection: 'column' }}>
                  <EditorGenerateInput workflowId={workflowId} />
                </div>
              </Sider>
            </ReactFlowProvider>
          </WorkflowRunningProvider>
        </Layout>
      </Layout>
    </SessionProvider>
  </WorkflowEditorProvider>
}

export default WorkflowEditor
