// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

export const mapKVToObject = (k: string[], v: string[]): Record<string, string> => {
  const obj: Record<string, string> = {};

  k.forEach((key, index) => {
    obj[key] = `${v[index] || ''}`
  });

  return obj;
};