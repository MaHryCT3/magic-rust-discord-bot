class LoopUnstableException(Exception):
    def __init__(self, seconds_de_jure, seconds_de_facto):
        self.seconds_de_jure = seconds_de_jure
        self.seconds_de_facto = seconds_de_facto
