"use client"
import { Message } from "@/models/chat/message"
import { Avatar, List } from "antd"
import { Session } from "next-auth"
import LunarImage from "@/assets/LogoSquare.png"
import ReactMarkdown from 'react-markdown'

interface ChatListProps {
  messages: Message[]
  session: Session
}

const ChatList: React.FC<ChatListProps> = ({ messages, session }) => {

  const renderContent = (content: string) => {
    // Regular expression to match base64 image strings
    const base64Pattern = /\((data:image\/[a-zA-Z]+;base64,[^\s)]+)\)/g;

    console.log('>>>', content.match(base64Pattern))

    const parts = content.split(base64Pattern).map((part, index) => {
      if (part.startsWith("data:image")) {
        // Render <img> tag for base64 content
        return <img key={index} src={part} alt="Embedded Base64" style={{ maxWidth: '100%' }} />;
      } else {
        // Render text parts as Markdown
        return <ReactMarkdown key={index}>{part}</ReactMarkdown>;
      }
    });

    return parts;
  };

  return <List
    style={{
      marginTop: 'auto',
    }}
    dataSource={messages}
    renderItem={(item, index) => (
      <>
        <List.Item key={index}>
          <List.Item.Meta
            avatar={<Avatar src={item.type === 'human' ? session.user?.image : LunarImage.src} />}
            title={item.type === 'human' ? session.user?.name ?? session.user?.email : 'Lunar'}
            description={renderContent(item.content)}
          />
        </List.Item>
      </>
    )}
  />
}

export default ChatList
