import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from khotla_chain import KhotlaChain


blockchain = KhotlaChain()


def calculate_balance(address):
    balance = 0.0

    for block in blockchain.chain:
        for transaction in block.transactions:
            sender = transaction.get("sender")
            receiver = transaction.get("receiver")
            amount = float(transaction.get("amount", 0))

            if receiver == address:
                balance += amount

            if sender == address:
                balance -= amount

    return balance


def block_to_dict(block):
    return {
        "index": block.index,
        "timestamp": block.timestamp,
        "transactions": block.transactions,
        "previous_hash": block.previous_hash,
        "nonce": block.nonce,
        "hash": block.hash
    }


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

    def do_GET(self):

        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":

            self.send_json({
                "name": "Khotla Testnet API",
                "coin": "Khotla Coin",
                "ticker": "KHT",
                "network": "Khotla Testnet",
                "status": "online"
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
                "latest_block": blockchain.latest_block().hash
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

            self.send_json({
                "address": address,
                "balance": calculate_balance(address),
                "currency": "KHT",
                "network": "Khotla Testnet"
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
                "length": len(blockchain.chain)
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

        if path == "/transaction":

            sender = data.get("sender")
            receiver = data.get("receiver")
            amount = data.get("amount")

            if not sender or not receiver:

                self.send_json({
                    "error": "Sender and receiver are required."
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

            if not sender.startswith("KHT"):

                self.send_json({
                    "error": "Invalid sender KHT address."
                }, 400)

                return

            if not receiver.startswith("KHT"):

                self.send_json({
                    "error": "Invalid receiver KHT address."
                }, 400)

                return

            sender_balance = calculate_balance(sender)

            if sender != "KHT_FAUCET":
                if amount > sender_balance:

                    self.send_json({
                        "error": "Insufficient KHT balance.",
                        "balance": sender_balance
                    }, 400)

                    return

            blockchain.add_transaction(
                sender,
                receiver,
                amount
            )

            self.send_json({
                "message": "Transaction added.",
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "currency": "KHT",
                "status": "pending"
            })

            return

        if path == "/mine":

            block = blockchain.mine()

            if block is None:

                self.send_json({
                    "message": "No pending transactions."
                })

                return

            self.send_json({
                "message": "Block mined successfully.",
                "block": block_to_dict(block)
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

            if not address.startswith("KHT"):

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

            blockchain.add_transaction(
                "KHT_FAUCET",
                address,
                amount
            )

            block = blockchain.mine()

            self.send_json({
                "message": "Testnet KHT sent.",
                "address": address,
                "amount": amount,
                "currency": "KHT",
                "block": block.index,
                "network": "Khotla Testnet"
            })

            return

        self.send_json({
            "error": "Endpoint not found."
        }, 404)


def run_server():

    host = "0.0.0.0"

    # Render provides PORT automatically.
    # Local testing uses 8080.
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
    print("      KHOTLA TESTNET API")
    print("================================")
    print()
    print("Network: Khotla Testnet")
    print("Coin: Khotla Coin")
    print("Ticker: KHT")
    print()
    print("API running on port:", port)
    print()
    print("Khotla Testnet API is running!")

    server.serve_forever()


if __name__ == "__main__":
    run_server()
