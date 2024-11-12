// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

"use client"
import { Message } from "@/models/chat/message"
import { Avatar, List } from "antd"
import LunarImage from "@/assets/LogoSquare.png"
import ReactMarkdown from 'react-markdown'
import GenericOutput from "../io/GenericOutput/GenericOutput"
import { useSession } from "next-auth/react"

interface ChatListProps {
  messages: Message[]
}

const ChatList: React.FC<ChatListProps> = ({ messages }) => {

  const session = useSession()

  const parseLunarTypeTag = (input: string) => {
    const regex = /<lunartype type="([^"]+)">([^<]+)<\/lunartype>/;
    const match = input.match(regex);

    if (match) {
      const [, type, label] = match;
      return { type, label };
    }

    return null;
  }

  const renderContent = (message: Message) => {
    const content = message.content
    const workfowOutput = message.workflows_output ?? {}
    const lunarTagPattern = /(<lunartype type="[^"]+">[^<]*<\/lunartype>)/g;
    const parts = content.split(lunarTagPattern).filter(Boolean).map((part, index) => {
      if (part.match(lunarTagPattern)) {
        const parsedResult = parseLunarTypeTag(part)
        if (!parsedResult) return <></>
        const { label } = parsedResult
        const componentModel = workfowOutput[label]
        return <GenericOutput
          workflowId={componentModel.workflowId ?? ""}
          outputDataType={componentModel.output.dataType}
          content={componentModel.output.value}
        />;
      } else {
        const content = part.replaceAll('TERMINATE', '')
        return <ReactMarkdown key={index}>{content}</ReactMarkdown>;
      }
    });

    return parts;
  };

  const userImage = session.data?.user?.image
  const userName = session.data?.user?.name
  const userEmail = session.data?.user?.email

  return <List
    style={{
      marginTop: 'auto',
    }}
    dataSource={messages}
    renderItem={(message, index) => (
      <>
        <List.Item key={index}>
          <List.Item.Meta
            avatar={<Avatar src={message.type === 'human' ? userImage : LunarImage.src} />}
            title={message.type === 'human' ? userName ?? userEmail : 'Lunar'}
            description={renderContent(message)}
          />
        </List.Item>
      </>
    )}
  />
}

export default ChatList
