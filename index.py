from crypt import crypt
from blockchain import Blockchain
import random

def addr(length=10):
    return "0x" + ''.join([random.choice('0123456789ABCDEF') for _ in range(length)])

def mine(blockchain, address):
    last_proof = blockchain.last_block.proof
    proof = Blockchain.Block.proof_of_work(last_proof, blockchain.difficulty)
    cryptocoin.mine_block(address, proof)

cryptocoin = Blockchain(target_time=(1, 1))

carter_address = addr()
tyson_address = addr()
miner_address = addr()

# Start everyone off with a bunch of coins
cryptocoin.add_transaction(sender=cryptocoin.ADDRESS, recipient=carter_address, amount=100)
cryptocoin.add_transaction(sender=cryptocoin.ADDRESS, recipient=tyson_address, amount=100)
cryptocoin.add_transaction(sender=cryptocoin.ADDRESS, recipient=miner_address, amount=100)

# Mine a block to save the transactions
mine(cryptocoin, miner_address)

# Make a bunch of transactions
for _ in range(random.randint(1, 10)):
    sender = random.choice([carter_address, tyson_address, miner_address])
    recipient = random.choice([carter_address, tyson_address, miner_address])
    amount = random.randint(1, 10)
    cryptocoin.add_transaction(sender, recipient, amount)

# Mine another block to save the transactions
mine(cryptocoin, miner_address)
mine(cryptocoin, miner_address)
mine(cryptocoin, miner_address)
mine(cryptocoin, miner_address)
mine(cryptocoin, miner_address)
mine(cryptocoin, miner_address)
mine(cryptocoin, miner_address)

# Check that nothing is wrong
print("Valid: {}".format(cryptocoin.is_valid()))

# Calculate everyone's balances
print("\nBalances:")
print(f"Carter ({carter_address}): {cryptocoin.get_balance(carter_address)}")
print(f"Tyson  ({tyson_address}): {cryptocoin.get_balance(tyson_address)}")
print(f"Miner  ({miner_address}): {cryptocoin.get_balance(miner_address)}")
print(f"Coins in existence: {-cryptocoin.get_balance(cryptocoin.ADDRESS)}")


# Save the logs
cryptocoin.log.save("index.py.log")
print(f"\nLog saved to index.py.log")
