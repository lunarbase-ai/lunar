import { EyeInvisibleOutlined, EyeOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import React, { useState } from 'react';

interface SecretProps {
  secret: string;
}

const SecretDisplay: React.FC<SecretProps> = ({ secret }) => {
  const [show, setShow] = useState<boolean>(false);

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <p>
        {show ? secret : '••••••••'}
      </p>
      <Button
        onClick={() => setShow(prev => !prev)}
        type='text'
        icon={show ? <EyeInvisibleOutlined /> : <EyeOutlined />}
      />
    </div>
  );
};

export default SecretDisplay;