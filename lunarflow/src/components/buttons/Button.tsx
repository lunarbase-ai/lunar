import React from 'react';
import { Button as AntdButton, ButtonProps } from 'antd';

export interface CustomButtonProps extends ButtonProps {
}

const Button: React.FC<CustomButtonProps> = ({ children, style, ...rest }) => {
  const primaryStyle = {
    paddingTop: 8,
    paddingBottom: 8,
    paddingLeft: 12,
    paddingRight: 12,
    borderRadius: 8,
    backgroundImage: 'linear-gradient(to right, #4DB1DD 0%, #4DB1DD  24%, #69C3E2  100%)',
    color: '#fff',
    backgroundSize: '200% auto',
    border: 0,
  }
  const secondaryStyle: React.CSSProperties = {
    border: 'double 2px transparent',
    borderRadius: '8px',
    backgroundImage: 'linear-gradient(white, white), radial-gradient(circle at top left, #4DB1DD, #69C3E2)',
    backgroundOrigin: 'border-box',
    backgroundClip: 'padding-box, border-box',
    fontWeight: 600,
    color: '#4DB1DD'
  }
  const disabledStyle = {
    backgroundImage: 'none',
    backgroundColor: '#f5f5f5',
    color: '#bfbfbf',
    borderColor: '#d9d9d9',
    cursor: 'not-allowed',
    opacity: 1,
  }
  return <AntdButton
    color='#4DB1DD'
    style={{
      ...(rest.type === 'primary' ? primaryStyle : secondaryStyle),
      ...(rest.disabled ? disabledStyle : {}),
      ...style,
    }}
    {...rest}
  >
    {children}
  </AntdButton>;
};

export default Button;
