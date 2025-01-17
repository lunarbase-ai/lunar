import os.path


class LocalFileConnection:
    def __init__(self, file_root: str, file_name: str, **kwargs):
        self.file_root = file_root
        self.file_name = file_name

    def read(self):
        with open(os.path.join(self.file_root, self.file_name), "r") as f:
            return f.read()

    def write(self, content: str):
        with open(os.path.join(self.file_root, self.file_name), "w") as f:
            f.write(content)
