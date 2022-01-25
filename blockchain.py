from block import Block
from logger import Logger
import json

BLOCKCHAIN_ADDRESS = "0x0000000000"

class Blockchain:
    Block = Block
    ADDRESS = BLOCKCHAIN_ADDRESS

    def __init__(self, chain=[], *args, target_time=(10, 30), difficulty=1):
        self.chain = chain
        self.transaction_pool = []
        self.difficulty = difficulty
        self.target_time = target_time
        self.log = Logger()
        if len(chain) == 0:
            self.create_genesis_block()

    def create_genesis_block(self):
        self.log("GENESIS")
        self.create_block(proof=0, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = Block(index=len(self.chain), proof=proof, previous_hash=previous_hash, data=self.transaction_pool, difficulty=self.difficulty)
        self.transaction_pool = []
        self.chain.append(block)
        self.log("BLOCK", index=block.index, proof=block.proof, timestamp=block.timestamp, transactions=len(block.data))
        return block

    def add_transaction(self, sender, recipient, amount):
        transaction = { "sender": sender, "recipient": recipient, "amount": amount }
        self.transaction_pool.append(transaction)
        self.log("TRANSACTION", sender=sender, recipient=recipient, amount=amount)
        return transaction


    def mine_block(self, miner_address, proof):
        if Block.is_valid_proof(proof, self.last_block.proof, self.difficulty) is False:
            self.log("MINING_ERROR", error="Invalid proof of work")
            return False
        self.log("MINING", miner_address=miner_address, proof=proof)
        previous_block = self.chain[-1]
        self.add_transaction(sender=BLOCKCHAIN_ADDRESS, recipient=miner_address, amount=self.calculate_reward())
        block = self.create_block(proof, previous_block.hash)
        self.difficulty = self.calculate_difficulty()
        return block

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for transaction in block.data:
                if transaction["sender"] == address:
                    balance -= transaction["amount"]
                if transaction["recipient"] == address:
                    balance += transaction["amount"]
        return balance

    def calculate_difficulty(self):
        # It should take about 30-60 seconds to mine a block. If it takes less time, increase the difficulty. If it takes more than 60 seconds, decrease the difficulty.
        if len(self.chain) < 3:
            self.log("DIFFICULTY", difficulty_type="INITIAL")
            return self.difficulty

        last_block_time = self.last_block.timestamp
        earlier_block_time = self.chain[-2].timestamp
        delta = round(last_block_time - earlier_block_time + 0.1, 2)
        if delta < self.target_time[0]:
            self.log("DIFFICULTY", difficulty_type="INCREASE", delta=delta, new_difficulty=self.difficulty + 1)
            return self.difficulty + 1
        elif delta > self.target_time[1]:
            self.log("DIFFICULTY", difficulty_type="DECREASE", delta=delta, new_difficulty=self.difficulty - 1)
            return self.difficulty - 1
        self.log("DIFFICULTY", difficulty_type="STABLE", delta=delta, new_difficulty=self.difficulty)
        return self.difficulty

    def calculate_reward(self):
        # We calculate the amount of coins to reward the miner using the formula: reward = difficulty / 2
        return self.difficulty // 2

    def is_valid(self):
        return Blockchain.is_valid_chain(self.chain)

    def is_valid_proof(self, proof):
        last_block = self.last_block
        return Block.is_valid_proof(proof, last_block.proof, self.difficulty)

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def is_valid_chain(chain):
        previous_block = chain[0]
        for block in chain[1:]:
            # Each block's hash must match the hash of the previous block
            if block.previous_hash != previous_block.hash:
                return False

            # Each block's hash should be correct based on it's content
            if block.hash != Block.hash(block):
                return False

            # Each block must have a valid proof
            if not Block.is_valid_proof(block.proof, previous_block.proof, block.difficulty):
                return False

            # The previous block should have come before the current block
            if block.timestamp <= previous_block.timestamp:
                return False

            previous_block = block
        return True

    def save(self, file="blockchain.json"):
        with open(file, "w") as f:
            json.dump(self.to_json(), f)

    def to_json(self):
        return {
            "chain": [block.to_json() for block in self.chain],
            "transaction_pool": [transaction for transaction in self.transaction_pool],
            "difficulty": self.difficulty,
            "target_time": self.target_time
        }

    @staticmethod
    def load(file="blockchain.json"):
        with open(file, "r") as f:
            data = json.load(f)
        if data.get("chain") == None or data.get("transaction_pool") == None: raise Exception("Invalid blockchain file")
        data["chain"] = [Block.from_json(block) for block in data["chain"]]
        blockchain = Blockchain(data["chain"], target_time=data.get("target_time", (10, 30)), difficulty=data.get("difficulty", 1))
        blockchain.transaction_pool = data["transaction_pool"]
        return blockchain
