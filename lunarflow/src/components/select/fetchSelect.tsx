import React, { useState } from 'react';
import { Select, Spin } from 'antd';
import type { SelectProps } from 'antd';

export interface DebounceSelectProps<ValueType = any>
  extends Omit<SelectProps<ValueType | ValueType[]>, 'options' | 'children'> {
  fetchOptions: () => Promise<ValueType[]>;
}

export default function FetchSelect<
  ValueType extends { key?: string; label: React.ReactNode; value: string | number } = any,
>({ fetchOptions, ...props }: DebounceSelectProps<ValueType>) {
  const [fetching, setFetching] = useState(false);
  const [options, setOptions] = useState<ValueType[]>([]);

  const fetchData = async () => {
    setOptions([]);
    setFetching(true);
    const data = await fetchOptions();
    setOptions(data);
    setFetching(false);
  };

  return (
    <Select
      labelInValue
      filterOption={false}
      onClick={() => fetchData()}
      notFoundContent={fetching ? <Spin size="small" /> : null}
      {...props}
      options={options}
    />
  );
}
