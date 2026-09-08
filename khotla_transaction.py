import hashlib
import json
import time


class KhotlaTransaction:
    def __init__(self, sender, receiver, amount, signature=None):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()
        self.signature = signature

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": self.signature
        }

    def transaction_hash(self):
        data = json.dumps(
            self.to_dict(),
            sort_keys=True
        )

        return hashlib.sha256(
            data.encode()
        ).hexdigest()

    def is_valid(self):
        if self.sender == "KHT_GENESIS":
            return True

        if not self.signature:
            return False

        if not self.receiver:
            return False

        return True


if __name__ == "__main__":
    transaction = KhotlaTransaction(
        "KHT_GENESIS",
        "THABISO_WALLET",
        1000
    )

    print("Khotla Transaction")
    print("------------------")
    print("Sender:", transaction.sender)
    print("Receiver:", transaction.receiver)
    print("Amount:", transaction.amount, "KHT")
    print("Valid:", transaction.is_valid())
    print("Hash:", transaction.transaction_hash())
