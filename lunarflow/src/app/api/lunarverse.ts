// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

import { lunarbaseUrl } from '@/configuration'
import axios, { AxiosInstance } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: lunarbaseUrl
})

api.interceptors.request.use(async config => {
  config.headers['Access-Control-Allow-Origin'] = '*'
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    return Promise.reject(error)
  }
)

export default api
