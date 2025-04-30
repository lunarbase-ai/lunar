// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: CC0-1.0

/** @type {import('next').NextConfig} */

const dotenv = require("dotenv")
const withSvgr = require('next-plugin-svgr');

const nextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: '10mb',
    },
  },
}

dotenv.config({ path: '../.env' })

module.exports = withSvgr(nextConfig)
