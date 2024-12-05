// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later
"use server"
import { lunarverseUrl } from "@/configuration";
import { DataSource, DataSourceType } from "@/models/dataSource/DataSource";
import { revalidatePath } from "next/cache";
import type { GetProp, UploadFile, UploadProps } from 'antd';

export type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

export const listDataSourcesAction = async (userId: string): Promise<DataSource[]> => {
  const localFile: DataSource = {
    id: "",
    name: "Local File",
    description: "a local file",
    type: "LOCAL_FILE",
    connectionAttributes: {},
  }
  return [localFile]
}

export const listDataSourceTypesAction = async (userId: string): Promise<DataSourceType[]> => {
  const localFileType: DataSourceType = {
    id: "LOCAL_FILE",
    name: "Local File",
    expectedConnectionAttributes: [],
  }
  return [localFileType]
}

export const deleteDataSourceAction = async (userId: string, dataSourceName: string): Promise<void> => {
  const response = await fetch(`${lunarverseUrl}/data_source/${dataSourceName}?user_id=${userId}`, {
    method: 'DELETE'
  });
  if (response.ok) {
    revalidatePath('/');
  } else {
    throw new Error('Failed to delete data source');
  }
}

export const createDataSourceAction = async (userId: string, dataSource: DataSource): Promise<void> => {
  return
}

export const uploadFileToDataSourceAction = async (userId: string, file: UploadFile, dataSourceId: string): Promise<DataSource> => {
  const formData = new FormData();
  formData.append('files', file as FileType);

  const response = await fetch(`${lunarverseUrl}/data_source/upload?user_id=${userId}&data_source_name=${dataSourceId}`, {
    method: 'POST',
    body: formData
  });
  if (response.ok) {
    const dataSource: DataSource = await response.json();
    return dataSource;
  } else {
    throw new Error('Failed to upload file to data source');
  }
}
