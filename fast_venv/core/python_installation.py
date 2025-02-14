# fast_venv/core/python_installation.py
class PythonInstallation:
    def __init__(self, version: str, executable: str):
        self.version = version
        self.executable = executable
        self.major_version = int(version.split('.')[0])
        self.minor_version = int(version.split('.')[1])

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "executable": self.executable
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PythonInstallation':
        return cls(data["version"], data["executable"])