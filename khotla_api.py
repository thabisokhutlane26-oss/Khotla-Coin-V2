import hashlib
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from khotla_chain import KhotlaChain


blockchain = KhotlaChain()


def block_to_dict(block):

    return {
        "index": block.index,
        "timestamp": block.timestamp,
        "transactions": block.transactions,
        "previous_hash": block.previous_hash,
        "nonce": block.nonce,
        "hash": block.hash
    }


def create_transaction_id(
    sender,
    receiver,
    amount
):

    data = (
        f"{sender}|"
        f"{receiver}|"
        f"{amount}|"
        f"{time.time_ns()}"
    )

    return hashlib.sha256(
        data.encode("utf-8")
    ).hexdigest()


def valid_address(address):

    return (
        isinstance(address, str)
        and address.startswith("KHT")
        and len(address) == 43
    )


class KhotlaAPI(BaseHTTPRequestHandler):

    def send_json(
        self,
        data,
        status=200
    ):

        response = json.dumps(
            data,
            indent=2
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.end_headers()

        self.wfile.write(response)

    def read_json(self):

        content_length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        if content_length == 0:
            return {}

        body = self.rfile.read(
            content_length
        )

        return json.loads(
            body.decode("utf-8")
        )

    def do_OPTIONS(self):

        self.send_response(200)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

    def do_GET(self):

        parsed = urlparse(self.path)
        path = parsed.path

        # --------------------------------
        # ROOT
        # --------------------------------

        if path == "/":

            self.send_json({
                "name": "Khotla Testnet API",
                "coin": "Khotla Coin",
                "ticker": "KHT",
                "network": "Khotla Testnet",
                "status": "online",
                "version": "2.1"
            })

            return

        # --------------------------------
        # STATUS
        # --------------------------------

        if path == "/status":

            self.send_json({
                "network": "Khotla Testnet",
                "coin": "Khotla Coin",
                "ticker": "KHT",
                "status": "online",
                "blocks": len(
                    blockchain.chain
                ),
                "pending_transactions": len(
                    blockchain.pending_transactions
                ),
                "latest_block": (
                    blockchain.latest_block().hash
                ),
                "chain_valid": (
                    blockchain.is_valid()
                )
            })

            return

        # --------------------------------
        # BALANCE
        # --------------------------------

        if path == "/balance":

            query = parse_qs(
                parsed.query
            )

            address = query.get(
                "address",
                [None]
            )[0]

            if not address:

                self.send_json({
                    "error": "Address is required."
                }, 400)

                return

            if not valid_address(address):

                self.send_json({
                    "error": "Invalid KHT address."
                }, 400)

                return

            balance = blockchain.get_balance(
                address
            )

            available_balance = (
                blockchain.get_available_balance(
                    address
                )
            )

            self.send_json({
                "address": address,
                "balance": balance,
                "available_balance": (
                    available_balance
                ),
                "currency": "KHT",
                "network": "Khotla Testnet"
            })

            return

        # --------------------------------
        # CHAIN
        # --------------------------------

        if path == "/chain":

            chain_data = []

            for block in blockchain.chain:

                chain_data.append(
                    block_to_dict(block)
                )

            self.send_json({
                "chain": chain_data,
                "length": len(chain_data),
                "valid": blockchain.is_valid()
            })

            return

        # --------------------------------
        # TRANSACTION LOOKUP
        # --------------------------------

        if path == "/transaction":

            query = parse_qs(
                parsed.query
            )

            transaction_id = query.get(
                "id",
                [None]
            )[0]

            if not transaction_id:

                self.send_json({
                    "error": (
                        "Transaction ID "
                        "is required."
                    )
                }, 400)

                return

            # Confirmed transaction

            for block in blockchain.chain:

                for transaction in block.transactions:

                    if (
                        transaction.get(
                            "transaction_id"
                        )
                        == transaction_id
                    ):

                        self.send_json({
                            "transaction": (
                                transaction
                            ),
                            "block": (
                                block.index
                            ),
                            "block_hash": (
                                block.hash
                            ),
                            "status": "confirmed"
                        })

                        return

            # Pending transaction

            for transaction in (
                blockchain.pending_transactions
            ):

                if (
                    transaction.get(
                        "transaction_id"
                    )
                    == transaction_id
                ):

                    self.send_json({
                        "transaction": (
                            transaction
                        ),
                        "status": "pending"
                    })

                    return

            self.send_json({
                "error": (
                    "Transaction not found."
                )
            }, 404)

            return

        # --------------------------------
        # WALLET TRANSACTION HISTORY
        # --------------------------------

        if path == "/history":

            query = parse_qs(
                parsed.query
            )

            address = query.get(
                "address",
                [None]
            )[0]

            if not address:

                self.send_json({
                    "error": "Address is required."
                }, 400)

                return

            if not valid_address(address):

                self.send_json({
                    "error": "Invalid KHT address."
                }, 400)

                return

            transactions = []

            # Confirmed transactions

            for block in blockchain.chain:

                for transaction in block.transactions:

                    if (
                        transaction.get(
                            "sender"
                        ) == address
                        or transaction.get(
                            "receiver"
                        ) == address
                    ):

                        transactions.append({
                            "transaction": (
                                transaction
                            ),
                            "block": (
                                block.index
                            ),
                            "block_hash": (
                                block.hash
                            ),
                            "status": "confirmed"
                        })

            # Pending transactions

            for transaction in (
                blockchain.pending_transactions
            ):

                if (
                    transaction.get(
                        "sender"
                    ) == address
                    or transaction.get(
                        "receiver"
                    ) == address
                ):

                    transactions.append({
                        "transaction": (
                            transaction
                        ),
                        "status": "pending"
                    })

            self.send_json({
                "address": address,
                "transactions": transactions,
                "count": len(transactions),
                "network": "Khotla Testnet"
            })

            return

        self.send_json({
            "error": "Endpoint not found."
        }, 404)

    def do_POST(self):

        parsed = urlparse(self.path)
        path = parsed.path

        try:

            data = self.read_json()

        except Exception:

            self.send_json({
                "error": "Invalid JSON."
            }, 400)

            return

        # --------------------------------
        # CREATE TRANSACTION
        # --------------------------------

        if path == "/transaction":

            sender = data.get(
                "sender"
            )

            receiver = data.get(
                "receiver"
            )

            amount = data.get(
                "amount"
            )

            signature = data.get(
                "signature"
            )

            public_key = data.get(
                "public_key"
            )

            if not sender or not receiver:

                self.send_json({
                    "error": (
                        "Sender and receiver "
                        "are required."
                    )
                }, 400)

                return

            if not valid_address(sender):

                self.send_json({
                    "error": (
                        "Invalid sender "
                        "KHT address."
                    )
                }, 400)

                return

            if not valid_address(receiver):

                self.send_json({
                    "error": (
                        "Invalid receiver "
                        "KHT address."
                    )
                }, 400)

                return

            try:

                amount = float(amount)

            except (TypeError, ValueError):

                self.send_json({
                    "error": (
                        "Amount must be "
                        "a number."
                    )
                }, 400)

                return

            if amount <= 0:

                self.send_json({
                    "error": (
                        "Amount must be "
                        "greater than zero."
                    )
                }, 400)

                return

            available_balance = (
                blockchain.get_available_balance(
                    sender
                )
            )

            if amount > available_balance:

                self.send_json({
                    "error": (
                        "Insufficient "
                        "KHT balance."
                    ),
                    "balance": (
                        blockchain.get_balance(
                            sender
                        )
                    ),
                    "available_balance": (
                        available_balance
                    )
                }, 400)

                return

            transaction_id = (
                data.get(
                    "transaction_id"
                )
                or create_transaction_id(
                    sender,
                    receiver,
                    amount
                )
            )

            try:

                transaction = (
                    blockchain.add_transaction(
                        sender=sender,
                        receiver=receiver,
                        amount=amount,
                        transaction_id=(
                            transaction_id
                        ),
                        signature=signature,
                        public_key=public_key
                    )
                )

            except ValueError as error:

                self.send_json({
                    "error": str(error)
                }, 400)

                return

            self.send_json({
                "message": (
                    "Transaction added."
                ),
                "transaction_id": (
                    transaction[
                        "transaction_id"
                    ]
                ),
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "currency": "KHT",
                "signature": signature,
                "public_key": public_key,
                "status": "pending",
                "network": "Khotla Testnet"
            })

            return

        # --------------------------------
        # MINE
        # --------------------------------

        if path == "/mine":

            try:

                block = blockchain.mine()

            except ValueError as error:

                self.send_json({
                    "error": str(error)
                }, 400)

                return

            if block is None:

                self.send_json({
                    "message": (
                        "No pending "
                        "transactions."
                    ),
                    "status": (
                        "nothing_to_mine"
                    )
                })

                return

            self.send_json({
                "message": (
                    "Block mined "
                    "successfully."
                ),
                "block": block_to_dict(
                    block
                ),
                "chain_valid": (
                    blockchain.is_valid()
                )
            })

            return

        # --------------------------------
        # TESTNET FAUCET
        # --------------------------------

        if path == "/faucet":

            address = data.get(
                "address"
            )

            amount = data.get(
                "amount",
                100
            )

            if not address:

                self.send_json({
                    "error": (
                        "Wallet address "
                        "is required."
                    )
                }, 400)

                return

            if not valid_address(address):

                self.send_json({
                    "error": (
                        "Invalid KHT "
                        "wallet address."
                    )
                }, 400)

                return

            try:

                amount = float(amount)

            except (TypeError, ValueError):

                self.send_json({
                    "error": (
                        "Amount must be "
                        "a number."
                    )
                }, 400)

                return

            if amount <= 0:

                self.send_json({
                    "error": (
                        "Amount must be "
                        "greater than zero."
                    )
                }, 400)

                return

            transaction_id = (
                create_transaction_id(
                    "KHT_GENESIS",
                    address,
                    amount
                )
            )

            try:

                blockchain.add_transaction(
                    sender="KHT_GENESIS",
                    receiver=address,
                    amount=amount,
                    transaction_id=(
                        transaction_id
                    ),
                    signature=None,
                    public_key=None
                )

                block = blockchain.mine()

            except ValueError as error:

                self.send_json({
                    "error": str(error)
                }, 400)

                return

            self.send_json({
                "message": (
                    "Testnet KHT sent."
                ),
                "transaction_id": (
                    transaction_id
                ),
                "address": address,
                "amount": amount,
                "currency": "KHT",
                "block": block.index,
                "block_hash": block.hash,
                "network": "Khotla Testnet",
                "status": "confirmed"
            })

            return

        self.send_json({
            "error": "Endpoint not found."
        }, 404)


def run_server():

    host = "0.0.0.0"

    port = int(
        os.environ.get(
            "PORT",
            "8080"
        )
    )

    server = HTTPServer(
        (host, port),
        KhotlaAPI
    )

    print("================================")
    print("       KHOTLA TESTNET API")
    print("================================")
    print()
    print("Network: Khotla Testnet")
    print("Coin: Khotla Coin")
    print("Ticker: KHT")
    print("Version: 2.1")
    print()
    print("API running on port:", port)
    print()
    print("Khotla Testnet API is running!")

    server.serve_forever()


if __name__ == "__main__":

    run_server()
