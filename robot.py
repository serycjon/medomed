from queue import Queue
from threading import Thread
from time import sleep

class Robot:
    def __init__(self, game):
        self.game = game
        self.responses = Queue()
        self.game.response_queue = self.responses

    def queue_clear(self):
        q = self.responses
        while not q.empty():
            try:
                q.get(False)
            except Empty:
                continue
            q.task_done()

    def send(self, command):
        self.queue_clear()

        self.game.command_queue.put(command)
        return self.responses.get(block=True)

    def turn(self, angle):
        return self.send(('turn', angle))

    def forward(self, distance):
        return self.send(('forward', distance))

    def status(self):
        return self.send(('status', ))

    def pick(self, item):
        return self.send(('pick', item))

    def drop(self, item_number):
        return self.send(('drop', item_number))

    def sleep(self, seconds):
        sleep(seconds)

    def worker(self):
        raise NotImplementedError("Subclasses must override worker()!")
        
    def run(self):
        self.thread = Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()
