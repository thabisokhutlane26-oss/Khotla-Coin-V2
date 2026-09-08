import hashlib
import secrets


class KhotlaWallet:
    def __init__(self):
        self.private_key = secrets.token_hex(32)

        self.public_key = hashlib.sha256(
            self.private_key.encode()
        ).hexdigest()

        self.address = "KHT" + hashlib.sha256(
            self.public_key.encode()
        ).hexdigest()[:40]

    def wallet_info(self):
        return {
            "address": self.address,
            "public_key": self.public_key
        }

    def sign_message(self, message):
        data = message + self.private_key

        return hashlib.sha256(
            data.encode()
        ).hexdigest()


if __name__ == "__main__":
    wallet = KhotlaWallet()

    print("Khotla Wallet")
    print("-------------")
    print("Address:", wallet.address)
    print("Public Key:", wallet.public_key)
    print()
    print("Wallet created successfully.")
