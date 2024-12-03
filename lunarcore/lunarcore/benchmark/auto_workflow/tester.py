import logging
import warnings

from typing import List

from lunarcore.core.typings.datatypes import File
from lunarcore.benchmark.auto_workflow.config import LOGGER_FILE_TESTER_TEMPLATE
from lunarcore.benchmark.auto_workflow.utils import empty_file

class Tester():
    def __init__(self, tester_name: str = None, logger: logging.Logger = None):
        self.tester_name = tester_name
        self.logger = logger or self._init_logger()

    def _init_logger(self):
        logger = logging.getLogger(f'{__name__}@{self.tester_name}')
        logger.setLevel(logging.DEBUG)
        if not self.tester_name:
            warnings.warn('Cannot find Tester name. Creating logfile in results directory!')
        logger_file_path = LOGGER_FILE_TESTER_TEMPLATE.format(
            tester_name=self.tester_name or ''
        )
        empty_file(logger_file_path)
        file_handler = logging.FileHandler(logger_file_path)
        logger.addHandler(file_handler)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        # stream_handler = logging.StreamHandler(sys.stdout)
        # logger.addHandler(stream_handler)
        return logger

    def run_test(self, test_name: str, intent: str, files: List[File]):
        raise NotImplementedError("Subclass must implement abstract method")