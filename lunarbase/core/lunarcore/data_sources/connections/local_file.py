import os.path


class LocalFileConnection:
    def __init__(self, file_root: str, **kwargs):
        self.file_root = file_root

    def read(self, filename: str):
        with open(os.path.join(self.file_root, filename), "r") as f:
            return f.read()

    def write(self, filename: str, content: str):
        with open(os.path.join(self.file_root, filename), "w") as f:
            f.write(content)
