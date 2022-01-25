import hashlib
import time

class Block:
    def __init__(self, index, proof, previous_hash, data, difficulty, timestamp=None):
        self.index = index
        self.proof = proof
        self.previous_hash = previous_hash
        self.data = data
        self.difficulty = difficulty
        self.timestamp = timestamp or time.time()
        self.hash = Block.hash(self)

    def __repr__(self):
        return f"Block({self.index}, {self.data})"

    @staticmethod
    def hash(block):
        block_string = str({ "index": block.index, "proof": block.proof, "previous_hash": block.previous_hash, "data": block.data, "difficulty": block.difficulty, "timestamp": block.timestamp })
        return hashlib.sha256(block_string.encode()).hexdigest()

    @staticmethod
    def proof_of_work(previous_proof, difficulty):
        proof = 0
        while Block.is_valid_proof(proof, previous_proof, difficulty) is False:
            proof += 1
        return proof

    @staticmethod
    def is_valid_proof(proof, previous_proof, difficulty):
        guess = f'{proof}{previous_proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty

    def to_json(self):
        return {
            "index": self.index,
            "proof": self.proof,
            "previous_hash": self.previous_hash,
            "data": self.data,
            "difficulty": self.difficulty,
            "timestamp": self.timestamp,
            "hash": self.hash
        }

    @staticmethod
    def from_json(data):
        return Block(data["index"], data["proof"], data["previous_hash"], data["data"], data["difficulty"], data["timestamp"])
