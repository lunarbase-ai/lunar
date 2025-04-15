// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { HTMLAttributes } from "react";
import { Handle as ReactflowHandle, HandleProps } from "reactflow";

// TODO: use color from theme
type HandleComponentProps = HandleProps & Omit<HTMLAttributes<HTMLDivElement>, 'id'>

const Handle: React.FC<HandleComponentProps> = ({ ...props }) => {
  return <ReactflowHandle {...props} style={{
    ...props.style, ...{
      width: 10,
      height: 10,
      border: 'solid 2px #3464DF',
      backgroundColor: 'white',
    }
  }} />
}

export default Handle
