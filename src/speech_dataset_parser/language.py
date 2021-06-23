from enum import IntEnum


class Language(IntEnum):
  IPA = 0
  ENG = 1
  CHN = 2
  GER = 3
  ES = 4
  IT = 5
  UK = 6
  RU = 7
  FR = 8
  PL = 9

  def __repr__(self):
    if self == self.IPA:
      return str("ipa")
    if self == self.ENG:
      return str("eng")
    if self == self.CHN:
      return str("chn")
    if self == self.GER:
      return str("ger")
    if self == self.ES:
      return str("es")
    if self == self.IT:
      return str("it")
    if self == self.UK:
      return str("uk")
    if self == self.RU:
      return str("ru")
    if self == self.FR:
      return str("fr")
    if self == self.PL:
      return str("pl")
    assert False


lang_dict = {repr(x): x for x in list(Language)}


def is_lang_from_str_supported(lang: str) -> bool:
  return lang in lang_dict


def get_lang_from_str(lang: str) -> Language:
  assert is_lang_from_str_supported(lang)
  return lang_dict[lang]
