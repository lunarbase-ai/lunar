// Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
// SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
//
// SPDX-License-Identifier: GPL-3.0-or-later

export class AuthenticationError extends Error {
  constructor(m: string) {
    super(m);
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}
