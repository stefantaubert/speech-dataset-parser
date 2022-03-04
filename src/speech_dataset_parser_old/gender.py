from enum import IntEnum


class Gender(IntEnum):
  MALE = 0
  FEMALE = 1

  def __repr__(self) -> str:
    if self == Gender.MALE:
      return str("male")
    if self == Gender.FEMALE:
      return str("female")
    assert False

  def __str__(self) -> str:
    if self == Gender.MALE:
      return str("M")
    if self == Gender.FEMALE:
      return str("F")
    assert False


gender_dict = {str(x): x for x in list(Gender)}


def is_gender_from_str_supported(gender: str) -> bool:
  return gender in gender_dict


def get_gender_from_str(gender: str) -> Gender:
  assert is_gender_from_str_supported(gender)
  return gender_dict[gender]
