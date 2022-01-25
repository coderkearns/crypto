#!/usr/bin/env python3

import hashlib
import requests
import time
import os

###### Constants ######
BASE_URL = os.environ.get("URL", "http://localhost:5000")
if BASE_URL.endswith("/"): BASE_URL = BASE_URL[:-1]
PREP_URL = BASE_URL + "/mineprep"
MINE_URL = BASE_URL + "/mine"

MINER_ADDRESS = os.environ.get("ADDRESS")
if not MINER_ADDRESS:
    print("ERROR: Please set the ADDRESS environment variable to your blockchain address.")
    print("ADDRESS={your address here, like 0x1234 or 0x1111, etc} python miner2.py")
    os._exit(1)

###### Proof of Work ######
def is_valid_proof(proof, previous_hash, difficulty):
    guess = f'{proof}{previous_hash}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:difficulty] == '0' * difficulty

def calculate_proof(previous_proof, difficulty):
    proof = 0
    while not is_valid_proof(proof, previous_proof, difficulty):
        print("[PROOF]", proof, end="\r")
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
        last_proof = prep_data["last_proof"]
        difficulty = prep_data["difficulty"]
        proof = calculate_proof(last_proof, difficulty)
        response = requests.post(MINE_URL, json={ "proof": proof, "address": MINER_ADDRESS }).json()
        if response.get("error"):
            print(f"[ERROR] {response.get('error')}")
            return False
        block = response["block"]
        reward = response["reward"]
        end_time = time.time()
        time_delta = round(end_time - start_time, 2)
        print(f"[SUCCESS] proof={proof}, time={time_delta}s, reward={reward}")
        return reward
    except Exception as e:
        # If the exception is a connection error from requests:
        if "ConnectionError" in str(e):
            print(f"[ERROR] Could not connect to the server. Waiting for 5 seconds...")
            time.sleep(5)
            return False


###### Main ######
def main():
    print(f"MINING at {BASE_URL}")
    print(f"-- STARTING MINER FOR {MINER_ADDRESS} --")
    mined = 0
    total_earned = 0
    while True:
        try:
            reward = mine()
            if reward:
                mined += 1
                total_earned += reward
        except KeyboardInterrupt:
            print("\n-- STOPPING MINER --")
            print(f"MINED {mined} BLOCKS")
            print(f"EARNED {total_earned} TOTAL COINS")
            break

if __name__ == "__main__":
    main()
