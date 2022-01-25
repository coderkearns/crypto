from flask import Flask, request, render_template
import socket, atexit
from blockchain import Blockchain

app = Flask(__name__)
# Check if blockchain.json exists
try:
    with open("blockchain.json", "r") as f:
        app.cryptocoin = Blockchain.load("blockchain.json")
except FileNotFoundError:
    app.cryptocoin = Blockchain(difficulty=1, target_time=(1, 1))


def debug():
    if app.debug:
        print(f"[{request.method}] {request.url}")

### ROUTES ###
@app.route("/")
def index():
    debug()
    return render_template("index.html")

@app.route("/api")
def api():
    debug()
    return {
        "address": app.cryptocoin.ADDRESS,
        "difficulty": app.cryptocoin.difficulty,
        "transactions": len(app.cryptocoin.transaction_pool),
        "blocks": len(app.cryptocoin.chain),
        "endpoints": ["/mineprep", "/mine", "/transactions", "/transactions/new", "/block/<int:index>", "/block/last", "/balance/<string:address>", "/validate", "/info"]
        }

@app.route("/mineprep")
def mineprep():
    debug()
    last_proof = app.cryptocoin.last_block.proof
    current_difficulty = app.cryptocoin.difficulty
    return { "last_proof": last_proof, "difficulty": current_difficulty }

@app.route("/mine", methods=["GET", "POST"])
def mine():
    debug()
    if request.method == "POST":
        miner_address = request.json["address"]
        proof = request.json["proof"]
    else:
        miner_address = request.args["address"]
        proof = request.args["proof"]

    # Make sure arguments exist
    if not miner_address: return {"error": "Missing address"}, 400
    if not proof: return {"error": "Missing proof"}, 400
    try:
        proof = int(proof)
    except:
        return {"error": "Proof must be an integer"}, 400

    # Validate proof
    if not app.cryptocoin.is_valid_proof(proof): return {"error": "Invalid proof"}, 400

    # Mine the block
    block = app.cryptocoin.mine_block(miner_address, proof)
    if not block: return {"error": "Mining failed"}, 400

    # Calculate the reward
    reward = block.data[-1]["amount"]

    return { "block": block.to_json(), "reward": reward }, 200

@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    debug()
    sender = request.json["sender"]
    recipient = request.json["recipient"]
    if not sender: return {"error": "Missing sender"}, 400
    if not recipient: return {"error": "Missing recipient"}, 400
    try:
        amount = int(request.json["amount"])
    except:
        return {"error": "Amount must be an integer"}, 400

    # Add the transaction
    transaction = app.cryptocoin.add_transaction(sender, recipient, amount)
    if not transaction: return {"error": "Transaction failed"}, 400

    return { "transaction": transaction }, 200

@app.route("/block/last", methods=["GET"])
def last_block():
    debug()
    return { "block": app.cryptocoin.last_block.to_json() }, 200

@app.route("/block/<int:index>", methods=["GET"])
def block(index):
    debug()
    if len(app.cryptocoin.chain) < index: return {"error": "Block not found"}, 404
    return { "block": app.cryptocoin.chain[index].to_json() }, 200

@app.route("/balance/<address>", methods=["GET"])
def balance(address):
    debug()
    return { "address": address, "balance": app.cryptocoin.get_balance(address) }, 200

@app.route("/validate", methods=["GET"])
def validate():
    debug()
    return { "valid": app.cryptocoin.is_valid() }, 200

@app.route("/transactions", methods=["GET"])
def transactions():
    debug()
    return { "transactions": app.cryptocoin.transaction_pool }, 200

@app.route("/info.json")
def info():
    debug()
    addresses = []
    for block in app.cryptocoin.chain:
        for transaction in block.data:
            addresses.append(transaction["sender"])
            addresses.append(transaction["recipient"])
    addresses = list(set(addresses))
    try:
        blockchain_index = addresses.index(app.cryptocoin.ADDRESS)
        del addresses[blockchain_index]
        total_coins = -app.cryptocoin.get_balance(app.cryptocoin.ADDRESS)
    except:
        total_coins = 0
    balances = {}
    for address in addresses:
        balances[address] = app.cryptocoin.get_balance(address)

    is_valid = app.cryptocoin.is_valid()

    return {
        "addresses": addresses,
        "balances": balances,
        "totalCoins": total_coins,
        "lastProof": app.cryptocoin.last_block.proof,
        "difficulty": app.cryptocoin.difficulty,
        "blocks": len(app.cryptocoin.chain),
        "transactions": len(app.cryptocoin.transaction_pool),
        "valid": is_valid
    }

if __name__ == "__main__":
    import waitress
    from os import environ

    HOST = environ.get("HOST", "localhost")
    PORT = environ.get("PORT", "5000")
    DEBUG = True if environ.get("DEBUG", "").lower() == "true" else False

    app.debug = DEBUG
    if DEBUG: print("DEBUG MODE ON")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, int(PORT)))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    atexit.register(lambda: sock.close())

    atexit.register(lambda: app.cryptocoin.save("blockchain.json"))

    print(f"Listening at http://{HOST}:{PORT}/")
    waitress.serve(app, sockets=[sock])
