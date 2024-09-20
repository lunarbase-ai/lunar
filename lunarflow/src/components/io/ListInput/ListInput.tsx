// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { Select } from "antd"

interface Props {
  value: string[] | ':undef:'
  onInputChange: (value: string[]) => void
}

const ListInput: React.FC<Props> = ({ value, onInputChange }) => {
  const valueArray = value === ':undef:' || undefined ? [] : value
  return <>
    <Select
      value={valueArray}
      onChange={(newValue) => {
        onInputChange(newValue)
      }}
      mode="tags"
    />
  </>
}

export default ListInput
