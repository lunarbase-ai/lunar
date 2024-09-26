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

export default function LoginForm() {
  const onFinishFailed = (errorInfo: any) => {
    console.log('Failed:', errorInfo);
  }

  return <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 40 }}>
    <Image alt="Lunar" src={Logo.src} width={272} height={132} />
    <Title level={2} style={{ color: '#fff' }}>Welcome to the <span>Lunarverse</span>!</Title>
    <div style={{ display: 'inline' }}>
      <Text style={{ color: '#fff' }}>
        If you are new here, please
      </Text>
      <Link href="https://lunarbase.ai/early-access.html" style={{ color: '#4DB1DD' }}> request early access</Link>
      <Text style={{ color: '#fff' }}>. Otherwise,</Text>
    </div>

    <Form
      name="basic"
      style={{ maxWidth: 400, marginLeft: 'auto', marginRight: 'auto', width: '100%', marginTop: 64 }}
      initialValues={{ remember: true }}
      onFinish={() => signIn('google', { callbackUrl: '/' })}
      onFinishFailed={onFinishFailed}
      autoComplete="off"
      layout="vertical"
    >
      <Button icon={<GoogleOutlined />} size="large" type="primary" htmlType="submit" style={{ width: '100%' }}>
        Login with Google
      </Button>
    </Form>
  </div>
}
