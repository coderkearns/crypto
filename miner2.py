#!/usr/bin/env python2

from __future__ import absolute_import
import hashlib
try:
    import requests
except ImportError:
    print "Please install the requests library to use this script:"
    print "pip install requests"
    exit()
import time
import os
import sys

###### Constants ######
BASE_URL = u"http://192.168.0.176:5000/"
PREP_URL = BASE_URL + u"mineprep"
MINE_URL = BASE_URL + u"mine"

MINER_ADDRESS = os.environ.get(u"ADDRESS")
if not MINER_ADDRESS:
    print "ERROR: Please set the ADDRESS environment variable to your blockchain address."
    print "ADDRESS={your address here, like 0x1234 or 0x1111, etc} python miner2.py"
    os._exit(1)

###### Proof of Work ######
def is_valid_proof(proof, previous_hash, difficulty):
    guess = (str(proof)+str(previous_hash)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:difficulty] == u'0' * difficulty

def calculate_proof(previous_proof, difficulty):
    proof = 0
    while not is_valid_proof(proof, previous_proof, difficulty):
        sys.stdout.write(u"[PROOF] {}\r".format(proof))
        proof += 1
    return proof

###### Mining ######
def prepare_mine():
    prep_data = requests.get(PREP_URL).json()
    return prep_data

def mine():
    try:
        start_time = time.time()
        prep_data = prepare_mine()
        last_proof = prep_data[u"last_proof"]
        difficulty = prep_data[u"difficulty"]
        proof = calculate_proof(last_proof, difficulty)
        response = requests.post(MINE_URL, json={ u"proof": proof, u"address": MINER_ADDRESS }).json()
        if response.get(u"error"):
            print "[ERROR] {}".format(response.get('error'))
            return False
        block = response[u"block"]
        reward = response[u"reward"]
        end_time = time.time()
        time_delta = round(end_time - start_time, 2)
        print "[SUCCESS] proof={}, time={}s, reward={}".format(proof, time_delta, reward)
        return reward
    except Exception, e:
        # If the exception is a connection error from requests:
        if u"ConnectionError" in unicode(e):
            print "[ERROR] Could not connect to the server. Waiting for 5 seconds..."
            time.sleep(5)
            return False


###### Main ######
def main():
    print "MINING at {}".format(BASE_URL)
    print "-- STARTING MINER FOR {} --".format(MINER_ADDRESS)
    mined = 0
    total_earned = 0
    while True:
        try:
            reward = mine()
            if reward:
                mined += 1
                total_earned += reward
        except KeyboardInterrupt:
            print u"\n-- STOPPING MINER --"
            print "MINED {} BLOCKS".format(mined)
            print "EARNED {} TOTAL COINS".format(total_earned)
            break

if __name__ == u"__main__":
    main()
