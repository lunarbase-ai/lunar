// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later
"use server"
import { DataSource, DataSourceCreationModel, DataSourceType } from "@/models/dataSource/DataSource";
import type { GetProp, UploadFile, UploadProps } from 'antd';
import api from "../api/lunarverse";

export type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

export const getDataSourcesAction = async (userId: string): Promise<DataSource[]> => {
  const { data } = await api.get<DataSource[]>(`/datasource?user_id=${userId}`)
  return data
}

export const getDataSourceTypesAction = async (userId: string): Promise<DataSourceType[]> => {
  const { data } = await api.get<DataSourceType[]>(`/datasource/types?user_id=${userId}`)
  console.log(">>>", data)
  return data
}

export const deleteDataSourceAction = async (userId: string, dataSourceId: string): Promise<void> => {
  try {
    await api.delete(`/datasource/${dataSourceId}?user_id=${userId}`)
  } catch (error) {
    console.error(error)
  }
  return
}

export const createDataSourceAction = async (userId: string, dataSource: DataSourceCreationModel): Promise<void> => {
  try {
    const result = await api.post(`/datasource?user_id=${userId}`, dataSource)
  } catch (error) {
    console.error(error)
  }
  return
}

export const uploadFileToDataSourceAction = async (userId: string, file: UploadFile, dataSourceId: string): Promise<string> => {
  const formData = new FormData();
  formData.append('files', file as FileType);
  const { data } = await api.post<string>(`/datasource/${dataSourceId}/upload?user_id=${userId}`, formData)
  return data
}
