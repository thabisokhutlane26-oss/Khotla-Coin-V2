import base64
import hashlib
import json
import time
import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey
)


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

        try:

            public_key_bytes = bytes.fromhex(
                self.public_key
            )

            if len(public_key_bytes) != 32:
                return False

            expected_address = (
                "KHT"
                + hashlib.sha256(
                    public_key_bytes
                ).hexdigest()[:40]
            )

            if expected_address != self.sender:
                return False

            signature_bytes = base64.b64decode(
                self.signature
            )

            public_key = (
                Ed25519PublicKey.from_public_bytes(
                    public_key_bytes
                )
            )

            public_key.verify(
                signature_bytes,
                self.transaction_hash().encode("utf-8")
            )

            return True

        except Exception:

            return False

    def is_valid(self):

        if not self.sender:
            return False

        if not self.receiver:
            return False

        if self.amount <= 0:
            return False

        if not self.transaction_id:
            return False

        return self.verify_signature()


if __name__ == "__main__":

    print("================================")
    print("     KHOTLA TRANSACTION")
    print("================================")
    print()
    print("Transaction module loaded.")
