from queue import Queue
from threading import Thread
from time import sleep
from pprint import pprint

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

class TestRobot(Robot):
    def worker(self):
        while True:
            status = self.status()
            pprint(status)
            sleep(2)
        
