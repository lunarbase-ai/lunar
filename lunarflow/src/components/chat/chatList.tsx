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
            description={item.type === 'human' ? item.content : <ReactMarkdown>{item.content}</ReactMarkdown>}
          />
        </List.Item>
      </>
    )}
  />
}

export default ChatList
