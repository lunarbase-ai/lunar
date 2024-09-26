"use client";

import { Button } from "antd";

interface Props {
  redirectToWorkflows: () => void
  children?: React.ReactNode
}

const RedirectButton: React.FC<Props> = ({ redirectToWorkflows, children }) => {
  return <Button
    type="link"
    style={{
      marginLeft: 'auto',
    }}
    onClick={() => redirectToWorkflows()}
  >
    {children}
  </Button>
}

export default RedirectButton;
