import hashlib
import secrets


class KhotlaWallet:

    def __init__(self, private_key=None):

        if private_key:
            self.private_key = private_key
        else:
            self.private_key = secrets.token_hex(32)

        self.public_key = self.generate_public_key()

        self.address = self.generate_address()

    def generate_public_key(self):

        return hashlib.sha256(
            self.private_key.encode("utf-8")
        ).hexdigest()

    def generate_address(self):

        address_hash = hashlib.sha256(
            self.public_key.encode("utf-8")
        ).hexdigest()

        return "KHT" + address_hash[:40]

    def sign_message(self, message):

        data = (
            self.private_key
            + str(message)
        )

        return hashlib.sha256(
            data.encode("utf-8")
        ).hexdigest()

    def verify_signature(
        self,
        message,
        signature
    ):

        if not signature:
            return False

        expected = self.sign_message(
            message
        )

        return secrets.compare_digest(
            expected,
            signature
        )

    def export(self):

        return {
            "address": self.address,
            "public_key": self.public_key,
            "private_key": self.private_key
        }


if __name__ == "__main__":

    wallet = KhotlaWallet()

    message = "Khotla Testnet Transaction"

    signature = wallet.sign_message(
        message
    )

    print("================================")
    print("       KHOTLA WALLET")
    print("================================")
    print()
    print("Address:", wallet.address)
    print("Public Key:", wallet.public_key)
    print("Private Key:", wallet.private_key)
    print()
    print("Message:", message)
    print("Signature:", signature)
    print()
    print(
        "Signature valid:",
        wallet.verify_signature(
            message,
            signature
        )
    )
