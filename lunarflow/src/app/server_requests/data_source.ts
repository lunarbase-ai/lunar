// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { lunarverseUrl } from "@/configuration";
import { DataSource } from "@/models/dataSource/DataSource";
import { revalidatePath } from "next/cache";
import type { GetProp, UploadFile, UploadProps } from 'antd';

export type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

export const listDataSources = async (userId: string) => {
  const response = await fetch(`${lunarverseUrl}/data_source/list?user_id=${userId}`);
  if (response.ok) {
    const data = await response.json();
    return data;
  } else {
    throw new Error('Failed to fetch data sources');
  }
}

export const deleteDataSource = async (userId: string, dataSourceName: string): Promise<void> => {
  const response = await fetch(`${lunarverseUrl}/data_source/${dataSourceName}?user_id=${userId}`, {
    method: 'DELETE'
  });
  if (response.ok) {
    revalidatePath('/');
  } else {
    throw new Error('Failed to delete data source');
  }
}

export const createDataSourceFromFiles = async (userId: string, files: UploadFile[], dataSourceName: string): Promise<DataSource> => {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i] as FileType);
  }
  const response = await fetch(`${lunarverseUrl}/data_source/upload?user_id=${userId}&data_source_name=${dataSourceName}`, {
    method: 'POST',
    body: formData
  });
  if (response.ok) {
    const dataSource: DataSource = await response.json();
    return dataSource;
  } else {
    throw new Error('Failed to create data source');
  }
}
