# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os


# .env path
DOTENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), ".env")

# Tester name
AUTOWORKFLOW_LABEL = 'auto_workflow'

# Keys of the ComponentOutput model
COMPONENT_OUTPUT_KEY = 'output'
COMPONENT_OUTPUT_VALUE_KEY = 'value'
COMPONENT_IS_TERMINAL_KEY = 'isTerminal'

# Auto-workflow user
# USER_ID = 'auto_workflow_tester_user'
USER_ID = 'admin'

# Timout for execution of workflow
EXECUTION_TIMEOUT = 180