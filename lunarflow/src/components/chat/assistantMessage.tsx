import { Message } from "ai";
import { Fragment, ReactNode } from "react";

type MessagePart = NonNullable<Message['parts']>[number];

interface AssistantMessageProps {
  message: Message
  messagePartRender: (messagePart: MessagePart, index: number) => ReactNode
}

const AssistantMessage: React.FC<AssistantMessageProps> = ({
  message,
  messagePartRender,
}) => {
  return <>
    {message.parts?.map((part, index) => <Fragment key={index}>
      {messagePartRender(part, index)}
    </Fragment>)}
  </>
}

export default AssistantMessage
