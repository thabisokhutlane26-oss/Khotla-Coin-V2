import hashlib
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from khotla_chain import KhotlaChain


blockchain = KhotlaChain()


def calculate_balance(address):
    balance = 0.0

    for block in blockchain.chain:
        for transaction in block.transactions:
            sender = transaction.get("sender")
            receiver = transaction.get("receiver")

            try:
                amount = float(transaction.get("amount", 0))
            except (TypeError, ValueError):
                continue

            if receiver == address:
                balance += amount

            if sender == address:
                balance -= amount

    return round(balance, 8)


def block_to_dict(block):
    return {
        "index": block.index,
        "timestamp": block.timestamp,
        "transactions": block.transactions,
        "previous_hash": block.previous_hash,
        "nonce": block.nonce,
        "hash": block.hash,
    }


def create_transaction_id(sender, receiver, amount):
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

    def send_json(self, data, status=200):
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

        if path == "/":
            self.send_json({
                "name": "Khotla Testnet API",
                "coin": "Khotla Coin",
                "ticker": "KHT",
                "network": "Khotla Testnet",
                "status": "online",
                "version": "2.0",
            })
            return

        if path == "/status":
            self.send_json({
                "network": "Khotla Testnet",
                "coin": "Khotla Coin",
                "ticker": "KHT",
                "status": "online",
                "blocks": len(blockchain.chain),
                "pending_transactions": len(
                    blockchain.pending_transactions
                ),
                "latest_block": blockchain.latest_block().hash,
                "chain_valid": blockchain.is_valid(),
            })
            return

        if path == "/balance":
            query = parse_qs(parsed.query)

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

            self.send_json({
                "address": address,
                "balance": calculate_balance(address),
                "currency": "KHT",
                "network": "Khotla Testnet",
            })
            return

        if path == "/chain":
            chain_data = []

            for block in blockchain.chain:
                chain_data.append(
                    block_to_dict(block)
                )

            self.send_json({
                "chain": chain_data,
                "length": len(chain_data),
                "valid": blockchain.is_valid(),
            })
            return

        if path == "/transaction":
            query = parse_qs(parsed.query)

            transaction_id = query.get(
                "id",
                [None]
            )[0]

            if not transaction_id:
                self.send_json({
                    "error": "Transaction ID is required."
                }, 400)
                return

            for block in blockchain.chain:
                for transaction in block.transactions:
                    if (
                        transaction.get("transaction_id")
                        == transaction_id
                    ):
                        self.send_json({
                            "transaction": transaction,
                            "block": block.index,
                            "block_hash": block.hash,
                            "status": "confirmed",
                        })
                        return

            self.send_json({
                "error": "Transaction not found."
            }, 404)
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

        if path == "/transaction":
            sender = data.get("sender")
            receiver = data.get("receiver")
            amount = data.get("amount")

            if not sender or not receiver:
                self.send_json({
                    "error": "Sender and receiver are required."
                }, 400)
                return

            if not valid_address(sender):
                self.send_json({
                    "error": "Invalid sender KHT address."
                }, 400)
                return

            if not valid_address(receiver):
                self.send_json({
                    "error": "Invalid receiver KHT address."
                }, 400)
                return

            try:
                amount = float(amount)
            except (TypeError, ValueError):
                self.send_json({
                    "error": "Amount must be a number."
                }, 400)
                return

            if amount <= 0:
                self.send_json({
                    "error": "Amount must be greater than zero."
                }, 400)
                return

            sender_balance = calculate_balance(sender)

            if amount > sender_balance:
                self.send_json({
                    "error": "Insufficient KHT balance.",
                    "balance": sender_balance,
                }, 400)
                return

            transaction_id = create_transaction_id(
                sender,
                receiver,
                amount
            )

            transaction = blockchain.add_transaction(
                sender,
                receiver,
                amount,
                transaction_id
            )

            self.send_json({
                "message": "Transaction added.",
                "transaction_id": transaction[
                    "transaction_id"
                ],
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "currency": "KHT",
                "status": "pending",
                "network": "Khotla Testnet",
            })
            return

        if path == "/mine":
            block = blockchain.mine()

            if block is None:
                self.send_json({
                    "message": "No pending transactions.",
                    "status": "nothing_to_mine",
                })
                return

            self.send_json({
                "message": "Block mined successfully.",
                "block": block_to_dict(block),
                "chain_valid": blockchain.is_valid(),
            })
            return

        if path == "/faucet":
            address = data.get("address")
            amount = data.get("amount", 100)

            if not address:
                self.send_json({
                    "error": "Wallet address is required."
                }, 400)
                return

            if not valid_address(address):
                self.send_json({
                    "error": "Invalid KHT wallet address."
                }, 400)
                return

            try:
                amount = float(amount)
            except (TypeError, ValueError):
                self.send_json({
                    "error": "Amount must be a number."
                }, 400)
                return

            if amount <= 0:
                self.send_json({
                    "error": "Amount must be greater than zero."
                }, 400)
                return

            transaction_id = create_transaction_id(
                "KHT_FAUCET",
                address,
                amount
            )

            blockchain.add_transaction(
                "KHT_FAUCET",
                address,
                amount,
                transaction_id
            )

            block = blockchain.mine()

            self.send_json({
                "message": "Testnet KHT sent.",
                "transaction_id": transaction_id,
                "address": address,
                "amount": amount,
                "currency": "KHT",
                "block": block.index,
                "block_hash": block.hash,
                "network": "Khotla Testnet",
                "status": "confirmed",
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
    print("Version: 2.0")
    print()
    print("API running on port:", port)
    print()
    print("Khotla Testnet API is running!")

    server.serve_forever()


if __name__ == "__main__":
    run_server()
