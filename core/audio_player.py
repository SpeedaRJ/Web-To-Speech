import simpleaudio as sa


class AudioPlayer:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.segment = sa.WaveObject.from_wave_file(filename)

    def play(self) -> None:
        player = self.segment.play()
        player.wait_done()
