from Queue import Queue
from threading import Thread
from time import sleep

class Robot:
    def __init__(self, game):
        self.game = game
        self.responses = Queue()
        self.game.response_queue = self.responses

    def send(self, command):
        self.game.command_queue.put(command)
        return self.responses.get(block=True)

    def turn(self, angle):
        return self.send(('turn', angle))

    def forward(self, distance):
        return self.send(('forward', distance))

    def status(self):
        return self.send(('status', ))

    def worker(self):
        raise NotImplementedError("Subclasses must override worker()!")
        
    def run(self):
        self.thread = Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()

class ZigZagRobot(Robot):
    def worker(self):
        sign = -1
        while True:
            self.forward(1)
            angle = self.status()['player']['rot'] + 90 * sign
            self.turn(angle)
            self.forward(1)
            angle = self.status()['player']['rot'] + 90 * sign
            self.turn(angle)
            sign = sign * -1
            sleep(1)
        
