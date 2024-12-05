// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later
"use server"
import { DataSource, DataSourceType } from "@/models/dataSource/DataSource";
import type { GetProp, UploadFile, UploadProps } from 'antd';
import api from "../api/lunarverse";

export type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

export const listDataSourcesAction = async (userId: string): Promise<DataSource[]> => {
  const { data } = await api.get<DataSource[]>(`/datasource?user_id=${userId}`)
  return data
}

export const listDataSourceTypesAction = async (userId: string): Promise<DataSourceType[]> => {
  const { data } = await api.get<DataSourceType[]>(`/datasource/types?user_id=${userId}`)
  return data
}

export const deleteDataSourceAction = async (userId: string, dataSourceId: string): Promise<void> => {
  await api.delete(`/datasource/${dataSourceId}?user_id=${userId}`)
  return
}

export const createDataSourceAction = async (userId: string, dataSource: DataSource): Promise<void> => {
  await api.post(`/datasource?user_id=${userId}`, dataSource)
  return
}

export const uploadFileToDataSourceAction = async (userId: string, file: UploadFile, dataSourceId: string): Promise<string> => {
  const formData = new FormData();
  formData.append('files', file as FileType);
  const { data } = await api.post<string>(`/datasource/${dataSourceId}/upload?user_id=${userId}`, formData)
  return data
}
