#!/usr/bin/python3

import threading
import queue
import socket
import random


class BotsState:
    def __init__(self, bot_file, port=22, threads=10):
        self.bot_file = bot_file
        self.port = int(port)
        self.threads = threads

        self.q = queue.Queue()
        self.bots = set()

    def status(self):
        self.create_threads()
        self.check_queue()
        bs = [bot for bot in self.bots]
        random.shuffle(bs)
        return bs

    def create_threads(self):
        for _ in range(self.threads):
            t = threading.Thread(target=self.work)
            t.daemon = True
            t.start()

    def check_queue(self):
        [self.q.put(bot) for bot in self.get_file(self.bot_file)]
        self.q.join()

    @staticmethod
    def get_file(filename):
        file = open(filename, "r")
        contents = file.read().splitlines()
        file.close()
        return contents

    def work(self):
        while True:
            bot = self.q.get()
            self.check_bot(bot)
            self.q.task_done()

    def check_bot(self, bot):
        # TODO: do this process through TOR
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        c = s.connect_ex((bot, self.port))
        s.close()
        self.bots.add(bot) if c == 0 else None
