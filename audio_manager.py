from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtMultimedia import QSoundEffect

class AudioManager:
    """کلاسی برای مدیریت بارگذاری و پخش جلوه‌های صوتی."""
    def __init__(self):
        self.sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        sound_files = {
            "play": "resources/audio/card_play.wav",
            "shuffle": "resources/audio/shuffle.wav",
            "win": "resources/audio/win_trick.wav"
        }
        
        for name, path in sound_files.items():
            file_info = QFileInfo(path)
            if not file_info.exists():
                print(f"هشدار: فایل صوتی پیدا نشد: {path}")
                continue
                
            sound_effect = QSoundEffect()
            sound_effect.setSource(QUrl.fromLocalFile(path))
            sound_effect.setVolume(0.8)
            self.sounds[name] = sound_effect

    def play(self, sound_name: str):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
