from enum import IntEnum


class Language(IntEnum):
  PL = 0
  ENG = 1
  CHN = 2
  GER = 3
  ES = 4
  IT = 5
  UK = 6
  RU = 7
  FR = 8

  def __repr__(self):
    if self == self.ENG:
      return str("English")
    if self == self.CHN:
      return str("Chinese")
    if self == self.GER:
      return str("German")
    if self == self.ES:
      return str("Spanish")
    if self == self.IT:
      return str("Italian")
    if self == self.UK:
      return str("Ukrainian")
    if self == self.RU:
      return str("Russian")
    if self == self.FR:
      return str("French")
    if self == self.PL:
      return str("Polish")
    assert False

  def __str__(self):
    if self == self.ENG:
      return str("ENG")
    if self == self.CHN:
      return str("CHN")
    if self == self.GER:
      return str("GER")
    if self == self.ES:
      return str("ES")
    if self == self.IT:
      return str("IT")
    if self == self.UK:
      return str("UK")
    if self == self.RU:
      return str("RU")
    if self == self.FR:
      return str("FR")
    if self == self.PL:
      return str("PL")
    assert False


lang_dict = {str(x): x for x in list(Language)}


def is_lang_from_str_supported(lang: str) -> bool:
  return lang in lang_dict


def get_lang_from_str(lang: str) -> Language:
  assert is_lang_from_str_supported(lang)
  return lang_dict[lang]
