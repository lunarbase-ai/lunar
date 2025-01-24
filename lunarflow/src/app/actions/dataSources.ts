// SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
//
// SPDX-FileContributor: Danilo Gusicuma <danilo@lunarbase.ai>
//
// SPDX-License-Identifier: GPL-3.0-or-later
"use server"
import { DataSource, DataSourceCreationModel, DataSourceType } from "@/models/dataSource/DataSource";
import api from "../api/lunarverse";
import axios, { AxiosError } from "axios";
const util = require('util')

export const getDataSourcesAction = async (userId: string): Promise<DataSource[]> => {
  try {
    const { data } = await api.get<DataSource[]>(`/datasource?user_id=${userId}`)
    return data
  } catch (error) {
    console.error(error)
    return []
  }
}

export const getDataSourceTypesAction = async (userId: string): Promise<DataSourceType[]> => {
  try {
    const { data } = await api.get<DataSourceType[]>(`/datasource/types?user_id=${userId}`)
    return data
  } catch (error) {
    console.error(error)
    return []
  }
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

export const uploadFileToDataSourceAction = async (userId: string, formData: FormData, dataSourceId: string): Promise<string> => {
  console.log(">>>AAA", formData)
  try {
    const { data } = await api.post<string>(`/datasource/${dataSourceId}/upload?user_id=${userId}`, formData)
    return data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError

      console.error(util.inspect(axiosError.response?.data, false, null, true /* enable colors */))
    } else {
      console.error(error)
    }
    return ''
  }
}
