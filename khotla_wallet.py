import base64
import hashlib
import secrets

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey
)


class KhotlaWallet:

    def __init__(self, private_key=None):

        if private_key:

            try:
                private_bytes = bytes.fromhex(
                    private_key
                )

                if len(private_bytes) != 32:
                    raise ValueError(
                        "Private key must be 32 bytes."
                    )

                self._private_key = (
                    Ed25519PrivateKey.from_private_bytes(
                        private_bytes
                    )
                )

            except Exception as error:

                raise ValueError(
                    "Invalid Ed25519 private key."
                ) from error

        else:

            self._private_key = (
                Ed25519PrivateKey.generate()
            )

        self.private_key = (
            self._private_key
            .private_bytes_raw()
            .hex()
        )

        self.public_key = (
            self._private_key
            .public_key()
            .public_bytes_raw()
            .hex()
        )

        self.address = self.generate_address()

    def generate_address(self):

        address_hash = hashlib.sha256(
            bytes.fromhex(
                self.public_key
            )
        ).hexdigest()

        return "KHT" + address_hash[:40]

    def sign_message(self, message):

        if not isinstance(
            message,
            str
        ):
            message = str(message)

        signature = self._private_key.sign(
            message.encode("utf-8")
        )

        return base64.b64encode(
            signature
        ).decode("ascii")

    def verify_signature(
        self,
        message,
        signature
    ):

        try:

            if not isinstance(
                message,
                str
            ):
                message = str(message)

            signature_bytes = (
                base64.b64decode(
                    signature
                )
            )

            public_key_bytes = bytes.fromhex(
                self.public_key
            )

            public_key = (
                Ed25519PublicKey.from_public_bytes(
                    public_key_bytes
                )
            )

            public_key.verify(
                signature_bytes,
                message.encode("utf-8")
            )

            return True

        except Exception:

            return False

    @staticmethod
    def verify_external_signature(
        message,
        signature,
        public_key
    ):

        try:

            signature_bytes = (
                base64.b64decode(
                    signature
                )
            )

            public_key_bytes = bytes.fromhex(
                public_key
            )

            public_key_object = (
                Ed25519PublicKey.from_public_bytes(
                    public_key_bytes
                )
            )

            public_key_object.verify(
                signature_bytes,
                message.encode("utf-8")
            )

            return True

        except Exception:

            return False

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
    print("       KHOTLA ED25519 WALLET")
    print("================================")
    print()

    print(
        "Address:",
        wallet.address
    )

    print(
        "Public Key:",
        wallet.public_key
    )

    print(
        "Private Key:",
        wallet.private_key
    )

    print()

    print(
        "Message:",
        message
    )

    print(
        "Signature:",
        signature
    )

    print()

    print(
        "Signature valid:",
        wallet.verify_signature(
            message,
            signature
        )
    )

    print(
        "External verification:",
        KhotlaWallet.verify_external_signature(
            message,
            signature,
            wallet.public_key
        )
    )
