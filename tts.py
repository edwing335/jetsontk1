# coding=utf-8
import ctypes

class loudspeaker(object):
  """docstring for Loudspeaker"""
  def __init__(self, device_id=1):
    self.device_id = device_id
    self.tts = ctypes.CDLL("./tts/tts.so")
    self.init_tts()

  def init_tts(self):
    self.tts.init_tts(self.device_id)

  def release_tts(self):
    self.tts.release_tts()

  def spreak(self, words):
    utf8_words = unicode(words, "utf8")
    gbk_words = utf8_words.encode('gbk')
    self.tts.spreak(gbk_words)

  def raise_alert(self):
    utf8_words = unicode("有人摔倒了", "utf8")
    gbk_words = utf8_words.encode('gbk')
    self.tts.speak(gbk_words)


if __name__ == "__main__":
  ls = Loudspeaker(1)
  ls.init_tts()
  ls.raise_alert()
  ls.release_tts()
else:
  pass
