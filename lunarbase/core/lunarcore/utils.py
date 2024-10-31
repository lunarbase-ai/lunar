# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

def to_camel(snake_case):
    words = snake_case.split("_")
    camel_case = words[0] + "".join(word.capitalize() for word in words[1:])
    return camel_case