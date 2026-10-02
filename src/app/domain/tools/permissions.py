from enum import StrEnum


class Permission(StrEnum):
    FILESYSTEM_READ = "filesystem.read"
    PYTHON_EXECUTE = "python.execute"
    DATABASE_READ = "database.read"
    DATABASE_WRITE = "database.write"
