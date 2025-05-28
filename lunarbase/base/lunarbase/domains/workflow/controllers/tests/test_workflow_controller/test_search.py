#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import pytest

class TestSearch:
    def test_searches_workflows(self, controller, config, mock_workflow_search_index):
        user_id = config.DEFAULT_USER_TEST_PROFILE

        result = controller.search("test", user_id)

        mock_workflow_search_index.search.assert_called_once_with("test", user_id)
        assert result == mock_workflow_search_index.search.return_value 