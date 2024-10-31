"use client"
import { Message } from "@/models/chat/message"
import { Avatar, List } from "antd"
import { Session } from "next-auth"
import LunarImage from "@/assets/LogoSquare.png"
import ReactMarkdown from 'react-markdown'
import GenericOutput from "../io/GenericOutput/GenericOutput"
import { ComponentDataType } from "@/models/component/ComponentModel"

interface ChatListProps {
  messages: Message[]
  session: Session
}

const ChatList: React.FC<ChatListProps> = ({ messages, session }) => {

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
        console.log('>>>', componentModel)
        return <GenericOutput workflowId={componentModel.workflowId ?? ""} outputDataType={componentModel.output.dataType} content={componentModel.output.value} />;
      } else {
        const content = part.replaceAll('TERMINATE', '')
        return <ReactMarkdown key={index}>{content}</ReactMarkdown>;
      }
    });

    return parts;
  };

  return <List
    style={{
      marginTop: 'auto',
    }}
    dataSource={messages}
    renderItem={(message, index) => (
      <>
        <List.Item key={index}>
          <List.Item.Meta
            avatar={<Avatar src={message.type === 'human' ? session.user?.image : LunarImage.src} />}
            title={message.type === 'human' ? session.user?.name ?? session.user?.email : 'Lunar'}
            description={renderContent(message)}
          />
        </List.Item>
      </>
    )}
  />
}

export default ChatList
