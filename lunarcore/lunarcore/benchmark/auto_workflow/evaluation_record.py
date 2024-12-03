# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import warnings

from collections import defaultdict
from typing import Dict, List

from lunarcore.benchmark.auto_workflow.config import (
    EVALUATION_CORRECTS_KEY,
    EVALUATION_EXECUTION_FINISHES_KEY,
    EVALUATION_TOTAL_KEY,
    EVALUATION_RECORD_STR_TEMPLATE,
    EVALUATION_RECORD_GROUP_STATS_STR,
    OUTPUTS_RECORD_STR,
    LEVEL2LABEL_TEMPLATE,
    LINE_CHART_LEVELS_FILE_TEMPLATE,
    SCATTER_3D_LEVELS_FILE_TEMPLATE,
)
from lunarcore.benchmark.auto_workflow.utils import (
    linechart,
    scatterplot3d,
)


class EvaluationRecord():
    class TestOutput():
        def __init__(self, test_name: str, evaluation_data: Dict,
                     levels: Dict[str, int], labels: List[str],
                     workflow_outputs: List = None,
                     is_correct: bool = False,
                     execution_finished: bool = False):
            self.test_name = test_name
            self.evaluation_data = evaluation_data
            self.levels = levels
            self.labels = labels
            self.workflow_outputs = workflow_outputs
            self.is_correct = is_correct
            self.execution_finished = execution_finished

        def register_result(self, workflow_outputs: List, is_correct: bool):
            self.workflow_outputs = workflow_outputs
            self.is_correct = is_correct
            self.execution_finished = True

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            outputs_str = OUTPUTS_RECORD_STR.format(
                test_name=self.test_name,
                workflow_outputs=self.workflow_outputs,
                evaluation_data=self.evaluation_data,
                is_correct=self.is_correct,
                execution_finished=self.execution_finished
            )
            return outputs_str

    def __init__(self):
        self.nr_correct = 0
        self.nr_execution_finishes = 0
        self.total = 0
        self.stats_per_group = defaultdict(
            lambda: {
                EVALUATION_CORRECTS_KEY: 0,
                EVALUATION_EXECUTION_FINISHES_KEY: 0,
                EVALUATION_TOTAL_KEY: 0
            }
        )
        self.tests_outputs = {}

    def register_test(self, test_name: str, levels: List[str],
                      labels: List[str], evaluation_data: Dict):
        self.total += 1
        for label in labels:
            self.stats_per_group[label][EVALUATION_TOTAL_KEY] += 1
        self.tests_outputs[test_name] = self.TestOutput(
            test_name,
            evaluation_data,
            levels,
            labels,
        )

    def register_result(self, test_name: str, labels: List[str], workflow_outputs: List,  is_correct: bool):
        self.nr_execution_finishes += 1
        if is_correct:
            self.nr_correct += 1
        for label in labels:
            self.stats_per_group[label][EVALUATION_EXECUTION_FINISHES_KEY] += 1
            if is_correct:
                self.stats_per_group[label][EVALUATION_CORRECTS_KEY] += 1
        self.tests_outputs[test_name].register_result(workflow_outputs, is_correct)

    def get_fraction(self, label: str = None, frac_execution_finishes: bool = False):
        if label:
            nr_correct = self.stats_per_group[label][EVALUATION_EXECUTION_FINISHES_KEY if frac_execution_finishes else EVALUATION_CORRECTS_KEY]
            total = self.stats_per_group[label][EVALUATION_TOTAL_KEY]
        else:
            nr_correct = self.nr_execution_finishes if frac_execution_finishes else self.nr_correct
            total = self.total    
        if total == 0:
            return None      # handle in another way?
        fraction = nr_correct/total
        return fraction
    
    def _min_max_level(self, level_name: str):
        INF = 10**10
        min_level = INF
        max_level = -INF
        for test_output_data in self.tests_outputs.values():
            levels_dict = test_output_data.levels
            min_level = min(min_level, levels_dict.get(level_name, min_level))
            max_level = max(max_level, levels_dict.get(level_name, max_level))
        return min_level, max_level

    def level_result_line_chart(self, level_name: str, title: str, xlabel: str,
                                xaxis_integers: bool = False, plot_dir: str = '',
                                xaxis_factor: int = 1):
        min_level, max_level = self._min_max_level(level_name)
        x = []
        y_execution_finishes = []
        y_corrects = []
        y_bar = []
        for level in range(min_level, max_level+1):
            label = LEVEL2LABEL_TEMPLATE.format(level_name=level_name, level=level)
            if label in self.stats_per_group:
                x.append(xaxis_factor*level)
                y_bar.append(self.stats_per_group[label][EVALUATION_TOTAL_KEY])
                y_corrects.append(self.get_fraction(label))
                y_execution_finishes.append(self.get_fraction(label, True))
        filename = LINE_CHART_LEVELS_FILE_TEMPLATE.format(level_name=level_name)
        filepath = os.path.join(plot_dir, filename)
        return linechart(x, [y_execution_finishes, y_corrects],
                        #  ['Avg. Component Run', 'Avg. Exec()'], title, xlabel,
                        #  ['Avg. Run', 'Avg. Correct'], title, xlabel,
                         ['Run Acc.', 'Answer Acc.'], title, xlabel,
                         'Percentage', filepath, xaxis_integers, xaxis_factor,
                         ys_bar=y_bar)

    def _levels_result_2d(self, level_name1: str, level_name2: str):
        levels_result_2d = defaultdict(
            lambda: {
                EVALUATION_CORRECTS_KEY: 0,
                EVALUATION_EXECUTION_FINISHES_KEY: 0,
                EVALUATION_TOTAL_KEY: 0
            }
        )
        for test_name, test_output_data in self.tests_outputs.items():
            if level_name1 in test_output_data.levels and level_name2 in test_output_data.levels:
                level1 = test_output_data.levels[level_name1]
                level2 = test_output_data.levels[level_name2]
                key = (level1, level2)
                levels_result_2d[key][EVALUATION_TOTAL_KEY] += 1
                if test_output_data.execution_finished:
                    levels_result_2d[key][EVALUATION_EXECUTION_FINISHES_KEY] += 1
                if test_output_data.is_correct:
                    levels_result_2d[key][EVALUATION_CORRECTS_KEY] += 1
            else:
                warnings.warn(f"Level '{level_name1}' and/or level '{level_name2}' not present in test '{test_name}'")
        return levels_result_2d

    def two_levels_3d_scatter(self, level_name1: str, level_name2: str,
                              title: str, xlabel: str, ylabel: str,
                              plot_execution_finishes: bool = False,
                              plot_dir: str = ''):
        levels_result_2d = self._levels_result_2d(level_name1, level_name2)
        x = []
        y = []
        z = []
        scatter_labels = []
        if plot_execution_finishes:
            numerator_key = EVALUATION_EXECUTION_FINISHES_KEY 
        else:
            numerator_key = EVALUATION_CORRECTS_KEY
        for (level1, level2), result_dict in levels_result_2d.items():
            total = result_dict[EVALUATION_TOTAL_KEY]
            if total != 0:
                x.append(level1)
                y.append(level2)
                z.append(result_dict[numerator_key]/total)
                scatter_labels.append(f'#{total}')
            else:
                warnings.warn('Skipping scatter plotting results for ({level_name1}, {level_name2}) = ({level1}, {level2}) due to zero division!')
        filename = SCATTER_3D_LEVELS_FILE_TEMPLATE.format(
            frac_type = 'execution_finishes' if plot_execution_finishes else 'corrects',
            level_name1=level_name1,
            level_name2=level_name2
        )
        filepath = os.path.join(plot_dir, filename)
        return scatterplot3d(x, y, z, title, xlabel, ylabel, 'Percentage',
                             filepath, scatter_labels, axis_integers=True)

    def __repr__(self):
        d = {
            'nr_correct': self.nr_correct,
            'nr_execution_finishes': self.nr_execution_finishes,
            'total': self.total,
            'stats_per_group': self.stats_per_group
        }
        return str(d)

    def __str__(self):
        group_stats_strs = []
        for group, group_data in self.stats_per_group.items():
            group_stats_str = EVALUATION_RECORD_GROUP_STATS_STR.format(
                group_name = group,
                nr_correct = group_data[EVALUATION_CORRECTS_KEY],
                nr_execution_finishes = group_data[EVALUATION_EXECUTION_FINISHES_KEY],
                total = group_data[EVALUATION_TOTAL_KEY],
                frac_correct = self.get_fraction(group),
                frac_execution_finishes = self.get_fraction(group, True)
            )
            group_stats_strs.append(group_stats_str)
        outputs_strs = [str(outputs) for outputs in self.tests_outputs.values()]
        res_str = EVALUATION_RECORD_STR_TEMPLATE.format(
            nr_correct = self.nr_correct,
            nr_execution_finishes = self.nr_execution_finishes,
            total = self.total,
            frac_correct = self.get_fraction(),
            frac_execution_finishes = self.get_fraction(frac_execution_finishes=True),
            group_stats_str = '\n'.join(group_stats_strs) or '[no groups]',
            tests_outputs = '\n'.join(outputs_strs)
        )
        return res_str