import { Message } from "ai"

interface UserMessageProps {
  message: Message
}

const UserMessage: React.FC<UserMessageProps> = ({ message }) => {
  return <div className="lunar-user-message" style={{
    backgroundColor: '#1E3257',
    paddingTop: 8,
    paddingBottom: 8,
    paddingLeft: 16,
    paddingRight: 16,
    borderRadius: 8,
    maxWidth: '90%',
    alignSelf: 'end',
    display: 'inline-block',
    position: 'relative'
  }}>
    {message.parts?.map((part, index) => part.type === "text" ? <p key={index} style={{ color: '#fff' }}>{part.text}</p> : <></>)}
  </div>
}

export default UserMessage
