// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { GoogleOutlined } from "@ant-design/icons";
import { Button, Form, Typography } from "antd"
import { signIn } from "next-auth/react";
import Image from "next/image"
import Logo from "@/assets/logo-header-dark.svg"

const { Title, Text, Link } = Typography

interface LoginFormProps {
  bypassAuthentication: boolean
}

const LoginForm: React.FC<LoginFormProps> = ({ bypassAuthentication }) => {
  const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
  }

  const handleFormSubmit = () => {
    if (bypassAuthentication) {
      signIn('credentials', { username: 'admin', callbackUrl: '/' })
      return
    }
    signIn('google', { callbackUrl: '/' })
    return
  }

  return <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 40 }}>
    <Image alt="Lunar" src={Logo.src} width={272} height={132} />
    <Title level={2} style={{ color: '#fff' }}>Welcome to the <span>Lunarverse</span>!</Title>

    <Form
      name="basic"
      style={{ maxWidth: 400, marginLeft: 'auto', marginRight: 'auto', width: '100%', marginTop: 64 }}
      initialValues={{ remember: true }}
      onFinish={handleFormSubmit}
      onFinishFailed={onFinishFailed}
      autoComplete="off"
      layout="vertical"
    >
      {bypassAuthentication
        ? <Button size="large" type="primary" htmlType="submit" style={{ width: '100%' }}>
          Start using Lunar
        </Button>
        : <Button icon={<GoogleOutlined />} size="large" type="primary" htmlType="submit" style={{ width: '100%' }}>
          Login with Google
        </Button>}
    </Form>
  </div>
}

export default LoginForm
