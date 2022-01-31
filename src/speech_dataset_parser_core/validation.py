
from pathlib import Path


class ValidationError():
  # pylint: disable=no-self-use
  @property
  def default_message(self) -> str:
    return ""


class InternalError(ValidationError):
  @property
  def default_message(self) -> str:
    return "Internal error!"


class DirectoryNotExistsError(ValidationError):
  def __init__(self, path: Path) -> None:
    super().__init__()
    self.path = path

  @classmethod
  def validate(cls, path: Path):
    if not path.is_dir():
      return cls(path)
    return None

  @property
  def default_message(self) -> str:
    return f"Directory \"{str(self.path.absolute())}\" does not exist!"


class DirectoryAlreadyExistsError(ValidationError):
  def __init__(self, path: Path) -> None:
    super().__init__()
    self.path = path

  @classmethod
  def validate(cls, path: Path):
    if path.is_dir():
      return cls(path)
    return None

  @property
  def default_message(self) -> str:
    return f"Directory \"{str(self.path.absolute())}\" already exists!"


class FileNotExistsError(ValidationError):
  def __init__(self, path: Path) -> None:
    super().__init__()
    self.path = path

  @classmethod
  def validate(cls, path: Path):
    if not path.is_file():
      return cls(path)
    return None

  @property
  def default_message(self) -> str:
    return f"File \"{str(self.path.absolute())}\" does not exist!"
