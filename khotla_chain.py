import hashlib
import json
import time


class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }

        encoded = json.dumps(
            data,
            sort_keys=True
        ).encode()

        return hashlib.sha256(encoded).hexdigest()

    def mine(self, difficulty=3):
        target = "0" * difficulty

        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()


class KhotlaChain:
    def __init__(self):
        self.difficulty = 3
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(
            0,
            [],
            "0"
        )

    def latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        transaction = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": time.time()
        }

        self.pending_transactions.append(transaction)

    def mine(self):
        if not self.pending_transactions:
            return None

        block = Block(
            len(self.chain),
            self.pending_transactions,
            self.latest_block().hash
        )

        block.mine(self.difficulty)

        self.chain.append(block)
        self.pending_transactions = []

        return block

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True


if __name__ == "__main__":
    chain = KhotlaChain()

    chain.add_transaction(
        "KHT_GENESIS",
        "THABISO_WALLET",
        1000
    )

    block = chain.mine()

    print("Khotla Chain started!")
    print("Block:", block.index)
    print("Hash:", block.hash)
    print("Chain valid:", chain.is_valid())
    print("KHT transferred:", 1000)
