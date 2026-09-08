import hashlib
import json
import os
import time


CHAIN_FILE = "khotla_chain_data.json"


class Block:

    def __init__(
        self,
        index,
        transactions,
        previous_hash,
        timestamp=None,
        nonce=0
    ):
        self.index = index

        self.timestamp = (
            timestamp
            if timestamp is not None
            else time.time()
        )

        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce

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
            sort_keys=True,
            separators=(",", ":")
        ).encode("utf-8")

        return hashlib.sha256(
            encoded
        ).hexdigest()

    def mine(self, difficulty=3):

        target = "0" * difficulty

        while not self.hash.startswith(target):

            self.nonce += 1

            self.hash = self.calculate_hash()


class KhotlaChain:

    def __init__(
        self,
        difficulty=3,
        storage_file=CHAIN_FILE
    ):

        self.difficulty = difficulty
        self.storage_file = storage_file

        loaded = self.load_chain()

        if loaded:

            self.chain = loaded

        else:

            self.chain = [
                self.create_genesis_block()
            ]

        self.pending_transactions = []

    def create_genesis_block(self):

        return Block(
            0,
            [],
            "0"
        )

    def latest_block(self):

        return self.chain[-1]

    def add_transaction(
        self,
        sender,
        receiver,
        amount,
        transaction_id=None,
        signature=None,
        public_key=None
    ):

        if not sender:
            raise ValueError(
                "Sender is required."
            )

        if not receiver:
            raise ValueError(
                "Receiver is required."
            )

        try:
            amount = float(amount)
        except (TypeError, ValueError):

            raise ValueError(
                "Amount must be a number."
            )

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero."
            )

        if not transaction_id:

            transaction_id = hashlib.sha256(
                (
                    f"{sender}"
                    f"{receiver}"
                    f"{amount}"
                    f"{time.time_ns()}"
                ).encode("utf-8")
            ).hexdigest()

        transaction = {
            "transaction_id": transaction_id,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": time.time(),
            "signature": signature,
            "public_key": public_key
        }

        self.pending_transactions.append(
            transaction
        )

        return transaction

    def validate_transaction(self, transaction):

        sender = transaction.get("sender")
        receiver = transaction.get("receiver")
        amount = transaction.get("amount")
        transaction_id = transaction.get(
            "transaction_id"
        )

        if not sender:
            return False

        if not receiver:
            return False

        if not transaction_id:
            return False

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False

        if amount <= 0:
            return False

        if sender == "KHT_GENESIS":
            return True

        signature = transaction.get(
            "signature"
        )

        public_key = transaction.get(
            "public_key"
        )

        if not signature:
            return False

        if not public_key:
            return False

        expected_address = (
            "KHT"
            + hashlib.sha256(
                public_key.encode("utf-8")
            ).hexdigest()[:40]
        )

        if expected_address != sender:
            return False

        return True

    def mine(self):

        if not self.pending_transactions:
            return None

        for transaction in self.pending_transactions:

            if not self.validate_transaction(
                transaction
            ):
                raise ValueError(
                    "Invalid transaction."
                )

        block = Block(
            len(self.chain),
            self.pending_transactions.copy(),
            self.latest_block().hash
        )

        block.mine(
            self.difficulty
        )

        self.chain.append(
            block
        )

        self.pending_transactions = []

        self.save_chain()

        return block

    def is_valid(self):

        if not self.chain:
            return False

        for i in range(
            1,
            len(self.chain)
        ):

            current = self.chain[i]
            previous = self.chain[i - 1]

            if (
                current.hash
                != current.calculate_hash()
            ):
                return False

            if (
                current.previous_hash
                != previous.hash
            ):
                return False

            if not current.hash.startswith(
                "0" * self.difficulty
            ):
                return False

            for transaction in current.transactions:

                if not self.validate_transaction(
                    transaction
                ):
                    return False

        return True

    def save_chain(self):

        data = []

        for block in self.chain:

            data.append({
                "index": block.index,
                "timestamp": block.timestamp,
                "transactions": block.transactions,
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
                "hash": block.hash
            })

        temporary_file = (
            self.storage_file + ".tmp"
        )

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

        os.replace(
            temporary_file,
            self.storage_file
        )

    def load_chain(self):

        if not os.path.exists(
            self.storage_file
        ):
            return None

        try:

            with open(
                self.storage_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            loaded_chain = []

            for item in data:

                block = Block(
                    item["index"],
                    item["transactions"],
                    item["previous_hash"],
                    item["timestamp"],
                    item["nonce"]
                )

                stored_hash = item.get(
                    "hash"
                )

                if stored_hash:
                    block.hash = stored_hash

                loaded_chain.append(
                    block
                )

            if not loaded_chain:
                return None

            return loaded_chain

        except Exception:

            return None


if __name__ == "__main__":

    chain = KhotlaChain()

    chain.add_transaction(
        "KHT_GENESIS",
        "THABISO_WALLET",
        1000
    )

    block = chain.mine()

    print(
        "Khotla Chain started!"
    )

    print(
        "Block:",
        block.index
    )

    print(
        "Hash:",
        block.hash
    )

    print(
        "Chain valid:",
        chain.is_valid()
    )

    print(
        "KHT transferred:",
        1000
    )
