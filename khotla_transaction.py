import hashlib
import json
import time
import uuid


class KhotlaTransaction:

    def __init__(
        self,
        sender,
        receiver,
        amount,
        signature=None,
        public_key=None,
        transaction_id=None,
        timestamp=None
    ):

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero."
            )

        self.transaction_id = (
            transaction_id
            or str(uuid.uuid4())
        )

        self.sender = sender
        self.receiver = receiver
        self.amount = float(amount)

        self.timestamp = (
            timestamp
            if timestamp is not None
            else time.time()
        )

        self.signature = signature
        self.public_key = public_key

    def signing_data(self):

        data = {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }

        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":")
        )

    def transaction_hash(self):

        return hashlib.sha256(
            self.signing_data().encode("utf-8")
        ).hexdigest()

    def to_dict(self):

        return {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "public_key": self.public_key
        }

    def verify_signature(self):

        if self.sender == "KHT_GENESIS":
            return True

        if not self.signature:
            return False

        if not self.public_key:
            return False

        expected_address_hash = hashlib.sha256(
            self.public_key.encode("utf-8")
        ).hexdigest()

        expected_address = (
            "KHT"
            + expected_address_hash[:40]
        )

        if expected_address != self.sender:
            return False

        return True

    def is_valid(self):

        if not self.sender:
            return False

        if not self.receiver:
            return False

        if self.amount <= 0:
            return False

        if not self.transaction_id:
            return False

        if self.sender == "KHT_GENESIS":
            return True

        return self.verify_signature()


if __name__ == "__main__":

    transaction = KhotlaTransaction(
        "KHT_GENESIS",
        "THABISO_WALLET",
        1000
    )

    print("================================")
    print("     KHOTLA TRANSACTION")
    print("================================")
    print()

    print(
        "Transaction ID:",
        transaction.transaction_id
    )

    print(
        "Sender:",
        transaction.sender
    )

    print(
        "Receiver:",
        transaction.receiver
    )

    print(
        "Amount:",
        transaction.amount,
        "KHT"
    )

    print(
        "Transaction Hash:",
        transaction.transaction_hash()
    )

    print(
        "Valid:",
        transaction.is_valid()
    )
