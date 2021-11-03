from threading import Thread
from playsound import playsound
from datetime import time, datetime
from os import path


class MyThread(Thread):
    def __init__(self, event, tme, data):
        Thread.__init__(self)
        self.stopped = event
        self.time = tme
        self.data = data
        self.data[0] = list(map(lambda x: time(int(x[:2]), int(x[3:])), self.data[0]))

    def run(self):
        while not self.stopped.wait(self.time):
            now = datetime.now()
            needed = time(now.hour, now.minute)
            if needed in self.data[0]:
                ind = self.data[0].index(needed)
                txt = self.data[1][ind]
                if path.exists(f'assets/music/{txt}.mp3'):
                    playsound(f'assets/music/{txt}.mp3')
                else:
                    playsound('assets/music/ring.mp3')
