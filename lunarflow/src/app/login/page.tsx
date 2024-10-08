// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import LoginForm from '@/components/LoginForm';
import { Layout } from 'antd';
import './stars.css'

export default function Login() {

  const bypassAuthentication = process.env.BYPASS_AUTHENTICATION === "true"

  return <Layout style={{ height: '100vh', width: '100vw', backgroundColor: '#000', overflow: 'hidden' }}>
    <div style={{
      position: 'absolute',
      overflow: 'hidden',
      height: '100vh',
      width: '100vw'
    }}>
      <div className="stars"></div>
      <div className="stars"></div>
      <div className="stars"></div>
      <div className="stars"></div>
      <div className="stars"></div>
      <div className="stars"></div>
      <div className="stars"></div>
      <div className="stars"></div>
      <div className="stars"></div>
    </div>
    <Layout style={{
      position: 'absolute',
      backgroundColor: 'transparent',
      top: '20%',
      left: 0,
      right: 0,
      marginRight: 0,
      marginLeft: 0,
    }}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        maxWidth: 800,
        width: '100%',
        flexGrow: 1,
        marginRight: 'auto',
        marginLeft: 'auto',
        gap: 8
      }}
      >
        <LoginForm bypassAuthentication={bypassAuthentication} />
      </div>
    </Layout>
  </Layout>
}
