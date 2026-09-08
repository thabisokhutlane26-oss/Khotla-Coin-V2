import base64
import hashlib
import json
import os
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey
)


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

    def get_balance(self, address):

        if not address:
            return 0.0

        balance = 0.0

        for block in self.chain:

            for transaction in block.transactions:

                sender = transaction.get(
                    "sender"
                )

                receiver = transaction.get(
                    "receiver"
                )

                try:

                    amount = float(
                        transaction.get(
                            "amount",
                            0
                        )
                    )

                except (TypeError, ValueError):

                    continue

                if receiver == address:

                    balance += amount

                if sender == address:

                    balance -= amount

        return round(
            balance,
            8
        )

    def get_pending_spend(self, address):

        if not address:
            return 0.0

        pending_spend = 0.0

        for transaction in self.pending_transactions:

            if transaction.get(
                "sender"
            ) != address:

                continue

            try:

                amount = float(
                    transaction.get(
                        "amount",
                        0
                    )
                )

            except (TypeError, ValueError):

                continue

            if amount > 0:

                pending_spend += amount

        return round(
            pending_spend,
            8
        )

    def get_available_balance(self, address):

        balance = self.get_balance(
            address
        )

        pending_spend = self.get_pending_spend(
            address
        )

        return round(
            balance - pending_spend,
            8
        )

    def add_transaction(
        self,
        sender,
        receiver,
        amount,
        transaction_id=None,
        signature=None,
        public_key=None,
        timestamp=None
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

        if sender != "KHT_GENESIS":

            available_balance = (
                self.get_available_balance(
                    sender
                )
            )

            if amount > available_balance:

                raise ValueError(
                    "Insufficient balance."
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

        if timestamp is None:

            timestamp = time.time()

        transaction = {
            "transaction_id": transaction_id,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": timestamp,
            "signature": signature,
            "public_key": public_key
        }

        if sender != "KHT_GENESIS":

            if not self.validate_transaction(
                transaction
            ):

                raise ValueError(
                    "Invalid transaction."
                )

        self.pending_transactions.append(
            transaction
        )

        return transaction

    def transaction_signing_data(
        self,
        transaction
    ):

        data = {
            "transaction_id": transaction.get(
                "transaction_id"
            ),
            "sender": transaction.get(
                "sender"
            ),
            "receiver": transaction.get(
                "receiver"
            ),
            "amount": float(
                transaction.get(
                    "amount"
                )
            ),
            "timestamp": transaction.get(
                "timestamp"
            )
        }

        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":")
        )

    def validate_transaction(
        self,
        transaction
    ):

        sender = transaction.get(
            "sender"
        )

        receiver = transaction.get(
            "receiver"
        )

        transaction_id = transaction.get(
            "transaction_id"
        )

        signature = transaction.get(
            "signature"
        )

        public_key = transaction.get(
            "public_key"
        )

        timestamp = transaction.get(
            "timestamp"
        )

        try:

            amount = float(
                transaction.get(
                    "amount"
                )
            )

        except (TypeError, ValueError):

            return False

        if not sender:
            return False

        if not receiver:
            return False

        if not transaction_id:
            return False

        if amount <= 0:
            return False

        if timestamp is None:
            return False

        if sender == "KHT_GENESIS":
            return True

        if not signature:
            return False

        if not public_key:
            return False

        try:

            public_key_bytes = bytes.fromhex(
                public_key
            )

            if len(public_key_bytes) != 32:
                return False

            expected_address = (
                "KHT"
                + hashlib.sha256(
                    public_key_bytes
                ).hexdigest()[:40]
            )

            if expected_address != sender:
                return False

            signature_bytes = base64.b64decode(
                signature,
                validate=True
            )

            if len(signature_bytes) != 64:
                return False

            signing_data = (
                self.transaction_signing_data(
                    transaction
                )
            )

            transaction_hash = hashlib.sha256(
                signing_data.encode("utf-8")
            ).hexdigest()

            public_key_object = (
                Ed25519PublicKey.from_public_bytes(
                    public_key_bytes
                )
            )

            public_key_object.verify(
                signature_bytes,
                transaction_hash.encode("utf-8")
            )

            return True

        except Exception:

            return False

    def mine(self):

        if not self.pending_transactions:

            return None

        for transaction in (
            self.pending_transactions
        ):

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

            for transaction in (
                current.transactions
            ):

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
        "THABISO_WALLET balance:",
        chain.get_balance(
            "THABISO_WALLET"
        ),
        "KHT"
    )

    print(
        "Chain valid:",
        chain.is_valid()
    )
