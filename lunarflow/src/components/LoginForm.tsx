// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { GithubOutlined, GoogleOutlined } from "@ant-design/icons";
import { Button, Form, Typography } from "antd"
import { signIn } from "next-auth/react";
import Image from "next/image"
import Logo from "@/assets/logo-header-dark.svg"

const { Title } = Typography

interface LoginFormProps {
  bypassAuthentication: boolean
  defaultUser: string
}

const LoginForm: React.FC<LoginFormProps> = ({ bypassAuthentication }) => {
  const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
  }

  const renderLoginButtons = () => {
    return <div>
      <Button icon={<GoogleOutlined />} size="large" type="primary" onClick={() => signIn('google', { callbackUrl: '/' })} style={{ width: '100%', marginBottom: 16 }}>
        Login with Google
      </Button>
      {/* <Button icon={<GithubOutlined />} size="large" type="primary" onClick={() => signIn('github', { callbackUrl: '/' })} style={{ width: '100%' }}>
        Login with Github
      </Button> */}
    </div>
  }

  return <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 40 }}>
    <Image alt="Lunar" src={Logo.src} width={272} height={132} />
    <Title level={2} style={{ color: '#fff' }}>Welcome to the <span>Lunarverse</span>!</Title>
    <Form
      name="basic"
      style={{ maxWidth: 400, marginLeft: 'auto', marginRight: 'auto', width: '100%', marginTop: 64 }}
      initialValues={{ remember: true }}
      onFinishFailed={onFinishFailed}
      autoComplete="off"
      layout="vertical"
    >
      {bypassAuthentication
        ? <Button size="large" type="primary" onClick={() => signIn('credentials', { username: 'admin', callbackUrl: '/' })} style={{ width: '100%' }}>
          Start using Lunar
        </Button>
        : renderLoginButtons()}
    </Form>
  </div>
}

export default LoginForm
