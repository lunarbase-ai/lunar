'use client'

import Icon from "@ant-design/icons";
import AvatarDropdown from "../AvatarDropdown";
import DataSourceSvg from "@/assets/icons/DataSource.svg";
import { iconStyle } from "./icons";
import { Divider, List, Popover, Typography } from "antd";
const { Text } = Typography

const data = [
  'Cytokine knowledge base',
  'Brazilian school construction data sources',
  'Grant List',
  'Gene List',
];

const ChatHeaderActions: React.FC = () => {
  return <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
    <Popover placement="bottomRight" style={{ margin: 8 }} content={
      <List
        header={<Text strong>Data sources</Text>}
        dataSource={data}
        renderItem={(item) => (
          <List.Item>
            {item}
          </List.Item>
        )}
      />
    }>
      <Icon style={iconStyle} component={DataSourceSvg} />
    </Popover>
    <AvatarDropdown />
  </div>
}

export default ChatHeaderActions;
