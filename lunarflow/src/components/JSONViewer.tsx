// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import ReactJson from "react-json-view"

interface JSONViewerProps {
  src: object
}

const JSONViewer: React.FC<JSONViewerProps> = ({ src }) => {
  return <div style={{ width: '100%', maxHeight: 350, overflowY: 'scroll', padding: 0 }}><ReactJson
    src={src}
    indentWidth={1}
    enableClipboard={true}
    displayDataTypes={false}
    displayObjectSize={false}
    collapsed={true}
  /></div>
}

export default JSONViewer