import html
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from khotla_chain import KhotlaChain


HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "10000"))

chain = KhotlaChain()


def json_response(handler, data, status=200):
    body = json.dumps(
        data,
        indent=2,
        default=str
    ).encode("utf-8")

    handler.send_response(status)
    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )
    handler.send_header(
        "Content-Length",
        str(len(body))
    )
    handler.send_header(
        "Access-Control-Allow-Origin",
        "*"
    )
    handler.end_headers()

    handler.wfile.write(body)


def read_json(handler):
    try:
        length = int(
            handler.headers.get(
                "Content-Length",
                "0"
            )
        )

        if length <= 0:
            return {}

        body = handler.rfile.read(length)

        return json.loads(
            body.decode("utf-8")
        )

    except Exception:
        return {}


def block_to_dict(block):
    return {
        "index": block.index,
        "timestamp": block.timestamp,
        "transactions": block.transactions,
        "previous_hash": block.previous_hash,
        "nonce": block.nonce,
        "hash": block.hash
    }


def all_transactions():
    transactions = []

    for block in chain.chain:

        for transaction in block.transactions:

            item = dict(transaction)

            item["block"] = block.index
            item["block_hash"] = block.hash

            transactions.append(item)

    return transactions


def find_transaction(transaction_id):
    for transaction in all_transactions():

        if (
            transaction.get(
                "transaction_id"
            )
            == transaction_id
        ):
            return transaction

    return None


def explorer_page():
    blocks = list(
        reversed(
            chain.chain
        )
    )

    transactions = all_transactions()

    recent_blocks = blocks[:12]

    block_rows = ""

    for block in recent_blocks:

        tx_count = len(
            block.transactions
        )

        block_rows += f"""
        <div class="card">
            <div class="row">
                <div>
                    <div class="title">
                        Block #{html.escape(str(block.index))}
                    </div>
                    <div class="muted">
                        {tx_count} transaction(s)
                    </div>
                </div>

                <div class="badge">
                    CONFIRMED
                </div>
            </div>

            <div class="hash">
                Hash:
                {html.escape(block.hash)}
            </div>

            <div class="hash">
                Previous:
                {html.escape(block.previous_hash)}
            </div>
        </div>
        """

    transaction_rows = ""

    for transaction in reversed(
        transactions[-12:]
    ):

        transaction_id = str(
            transaction.get(
                "transaction_id",
                ""
            )
        )

        sender = str(
            transaction.get(
                "sender",
                ""
            )
        )

        receiver = str(
            transaction.get(
                "receiver",
                ""
            )
        )

        amount = transaction.get(
            "amount",
            0
        )

        block_number = transaction.get(
            "block",
            "-"
        )

        transaction_rows += f"""
        <div class="card">
            <div class="title">
                {html.escape(transaction_id)}
            </div>

            <div class="txline">
                <span>Amount</span>
                <strong>
                    {html.escape(str(amount))} KHT
                </strong>
            </div>

            <div class="txline">
                <span>From</span>
                <span class="hash">
                    {html.escape(sender)}
                </span>
            </div>

            <div class="txline">
                <span>To</span>
                <span class="hash">
                    {html.escape(receiver)}
                </span>
            </div>

            <div class="txline">
                <span>Block</span>
                <span>
                    #{html.escape(str(block_number))}
                </span>
            </div>
        </div>
        """

    if not block_rows:
        block_rows = """
        <div class="empty">
            No blocks yet.
        </div>
        """

    if not transaction_rows:
        transaction_rows = """
        <div class="empty">
            No transactions yet.
        </div>
        """

    valid = chain.is_valid()

    status_text = (
        "VALID"
        if valid
        else "INVALID"
    )

    status_class = (
        "good"
        if valid
        else "bad"
    )

    latest = chain.latest_block()

    page = f"""
<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
      content="width=device-width,
               initial-scale=1">

<title>Khotla Explorer</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: #07100b;
    color: #ffffff;
    font-family:
        Arial,
        Helvetica,
        sans-serif;
}}

.header {{
    padding: 28px 18px 22px;
    background:
        linear-gradient(
            180deg,
            #0d2115,
            #07100b
        );
    border-bottom:
        1px solid #183b23;
}}

.logo {{
    font-size: 27px;
    font-weight: bold;
}}

.logo span {{
    color: #35e875;
}}

.subtitle {{
    color: #91a999;
    margin-top: 6px;
}}

.container {{
    max-width: 900px;
    margin: auto;
    padding: 18px;
}}

.search {{
    width: 100%;
    padding: 15px;
    border-radius: 12px;
    border:
        1px solid #275c37;
    background: #0d1b12;
    color: white;
    font-size: 16px;
    margin-bottom: 18px;
}}

.stats {{
    display: grid;
    grid-template-columns:
        repeat(2, 1fr);
    gap: 12px;
}}

.stat {{
    background: #0d1b12;
    border:
        1px solid #183b23;
    border-radius: 14px;
    padding: 17px;
}}

.stat-number {{
    font-size: 25px;
    font-weight: bold;
    color: #35e875;
}}

.stat-label {{
    margin-top: 5px;
    color: #91a999;
    font-size: 13px;
}}

.section {{
    margin-top: 26px;
}}

.section-title {{
    font-size: 21px;
    font-weight: bold;
    margin-bottom: 12px;
}}

.card {{
    background: #0d1b12;
    border:
        1px solid #183b23;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 11px;
}}

.row {{
    display: flex;
    justify-content:
        space-between;
    gap: 10px;
}}

.title {{
    font-weight: bold;
    word-break: break-all;
}}

.muted {{
    color: #91a999;
    margin-top: 5px;
    font-size: 13px;
}}

.badge {{
    color: #07100b;
    background: #35e875;
    padding: 5px 8px;
    border-radius: 7px;
    font-size: 11px;
    font-weight: bold;
    height: fit-content;
}}

.hash {{
    color: #75c58f;
    word-break: break-all;
    font-size: 12px;
}}

.txline {{
    display: flex;
    justify-content:
        space-between;
    gap: 15px;
    margin-top: 10px;
    color: #91a999;
}}

.txline strong {{
    color: #35e875;
}}

.network {{
    margin-top: 16px;
    padding: 13px;
    border-radius: 12px;
    background: #0d1b12;
    border:
        1px solid #183b23;
}}

.dot {{
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #35e875;
    margin-right: 7px;
}}

.good {{
    color: #35e875;
    font-weight: bold;
}}

.bad {{
    color: #ff5f5f;
    font-weight: bold;
}}

.empty {{
    color: #91a999;
    padding: 20px;
    text-align: center;
}}

.footer {{
    text-align: center;
    color: #617667;
    padding: 35px 15px;
    font-size: 13px;
}}

@media (min-width: 700px) {{

    .stats {{
        grid-template-columns:
            repeat(4, 1fr);
    }}

}}

</style>

</head>

<body>

<div class="header">

    <div class="container">

        <div class="logo">
            KHOTLA <span>EXPLORER</span>
        </div>

        <div class="subtitle">
            Public blockchain explorer
        </div>

        <div class="network">
            <span class="dot"></span>
            Khotla Testnet
            —
            <span class="good">
                ONLINE
            </span>
        </div>

    </div>

</div>


<div class="container">

    <input
        class="search"
        placeholder=
        "Search by transaction ID or address..."
        onkeydown="
        if(event.key === 'Enter')
        {{
            const value =
                this.value.trim();

            if(value)
            {{
                window.location.href =
                    '/transaction?id=' +
                    encodeURIComponent(value);
            }}
        }}
        "
    >


    <div class="stats">

        <div class="stat">
            <div class="stat-number">
                {len(chain.chain)}
            </div>
            <div class="stat-label">
                BLOCKS
            </div>
        </div>

        <div class="stat">
            <div class="stat-number">
                {len(transactions)}
            </div>
            <div class="stat-label">
                TRANSACTIONS
            </div>
        </div>

        <div class="stat">
            <div class="stat-number">
                {len(chain.pending_transactions)}
            </div>
            <div class="stat-label">
                PENDING
            </div>
        </div>

        <div class="stat">
            <div class="stat-number {status_class}">
                {status_text}
            </div>
            <div class="stat-label">
                CHAIN STATUS
            </div>
        </div>

    </div>


    <div class="section">

        <div class="section-title">
            Latest Block
        </div>

        <div class="card">

            <div class="row">

                <div>
                    <div class="title">
                        Block #{latest.index}
                    </div>

                    <div class="muted">
                        Latest Khotla Chain block
                    </div>
                </div>

                <div class="badge">
                    CONFIRMED
                </div>

            </div>

            <div class="hash">
                Hash:
                {html.escape(latest.hash)}
            </div>

            <div class="hash">
                Previous:
                {html.escape(latest.previous_hash)}
            </div>

        </div>

    </div>


    <div class="section">

        <div class="section-title">
            Recent Blocks
        </div>

        {block_rows}

    </div>


    <div class="section">

        <div class="section-title">
            Recent Transactions
        </div>

        {transaction_rows}

    </div>

</div>


<div class="footer">

    Khotla Coin (KHT)

    <br>

    Khotla Chain • Khotla Testnet

    <br><br>

    Testnet only — not real money.

</div>

</body>

</html>
"""

    return page.encode("utf-8")


class KhotlaAPI(BaseHTTPRequestHandler):

    def send_html(self, content, status=200):

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(content))
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.end_headers()

        self.wfile.write(content)


    def do_OPTIONS(self):

        self.send_response(204)

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

        parsed = urlparse(
            self.path
        )

        path = parsed.path

        query = parse_qs(
            parsed.query
        )


        if path == "/":

            json_response(
                self,
                {
                    "name":
                        "Khotla Testnet API",

                    "coin":
                        "Khotla Coin",

                    "ticker":
                        "KHT",

                    "network":
                        "Khotla Testnet",

                    "status":
                        "online",

                    "version":
                        "2.2"
                }
            )

            return


        if path == "/status":

            json_response(
                self,
                {
                    "name":
                        "Khotla Testnet API",

                    "coin":
                        "Khotla Coin",

                    "ticker":
                        "KHT",

                    "network":
                        "Khotla Testnet",

                    "status":
                        "online",

                    "version":
                        "2.2"
                }
            )

            return


        if path == "/explorer":

            self.send_html(
                explorer_page()
            )

            return


        if path == "/chain":

            json_response(
                self,
                {
                    "chain":
                    [
                        block_to_dict(block)
                        for block in chain.chain
                    ],

                    "pending_transactions":
                        chain.pending_transactions,

                    "valid":
                        chain.is_valid()
                }
            )

            return


        if path == "/balance":

            address = query.get(
                "address",
                [None]
            )[0]

            if not address:

                json_response(
                    self,
                    {
                        "error":
                            "Address is required."
                    },
                    400
                )

                return

            balance = chain.get_balance(
                address
            )

            available = (
                chain.get_available_balance(
                    address
                )
            )

            json_response(
                self,
                {
                    "address":
                        address,

                    "balance":
                        balance,

                    "available_balance":
                        available,

                    "ticker":
                        "KHT"
                }
            )

            return


        if path == "/history":

            address = query.get(
                "address",
                [None]
            )[0]

            transactions = all_transactions()

            if address:

                transactions = [
                    transaction
                    for transaction in transactions

                    if (
                        transaction.get("sender")
                        == address

                        or

                        transaction.get("receiver")
                        == address
                    )
                ]

            json_response(
                self,
                {
                    "address":
                        address,

                    "transactions":
                        transactions
                }
            )

            return


        if path == "/transaction":

            transaction_id = query.get(
                "id",
                [None]
            )[0]

            if not transaction_id:

                json_response(
                    self,
                    {
                        "error":
                            "Transaction ID is required."
                    },
                    400
                )

                return

            transaction = find_transaction(
                transaction_id
            )

            if transaction is None:

                json_response(
                    self,
                    {
                        "error":
                            "Transaction not found."
                    },
                    404
                )

                return

            json_response(
                self,
                transaction
            )

            return


        json_response(
            self,
            {
                "error":
                    "Endpoint not found."
            },
            404
        )


    def do_POST(self):

        parsed = urlparse(
            self.path
        )

        path = parsed.path

        data = read_json(
            self
        )


        if path == "/transaction":

            try:

                transaction = (
                    chain.add_transaction(
                        sender=data.get(
                            "sender"
                        ),

                        receiver=data.get(
                            "receiver"
                        ),

                        amount=data.get(
                            "amount"
                        ),

                        transaction_id=data.get(
                            "transaction_id"
                        ),

                        signature=data.get(
                            "signature"
                        ),

                        public_key=data.get(
                            "public_key"
                        ),

                        timestamp=data.get(
                            "timestamp"
                        )
                    )
                )

                json_response(
                    self,
                    {
                        "success":
                            True,

                        "message":
                            "Transaction added.",

                        "transaction":
                            transaction
                    }
                )

            except Exception as error:

                json_response(
                    self,
                    {
                        "success":
                            False,

                        "error":
                            str(error)
                    },
                    400
                )

            return


        if path == "/mine":

            try:

                block = chain.mine()

                if block is None:

                    json_response(
                        self,
                        {
                            "success":
                                False,

                            "error":
                                "No pending transactions."
                        },
                        400
                    )

                    return

                json_response(
                    self,
                    {
                        "success":
                            True,

                        "message":
                            "Block mined.",

                        "block":
                            block_to_dict(block)
                    }
                )

            except Exception as error:

                json_response(
                    self,
                    {
                        "success":
                            False,

                        "error":
                            str(error)
                    },
                    400
                )

            return


        if path == "/faucet":

            address = data.get(
                "address"
            )

            if not address:

                json_response(
                    self,
                    {
                        "success":
                            False,

                        "error":
                            "Address is required."
                    },
                    400
                )

                return

            amount = 100

            try:

                transaction = (
                    chain.add_transaction(
                        sender="KHT_GENESIS",
                        receiver=address,
                        amount=amount
                    )
                )

                block = chain.mine()

                json_response(
                    self,
                    {
                        "success":
                            True,

                        "message":
                            "Faucet KHT sent.",

                        "amount":
                            amount,

                        "address":
                            address,

                        "transaction":
                            transaction,

                        "block":
                            block_to_dict(block)
                    }
                )

            except Exception as error:

                json_response(
                    self,
                    {
                        "success":
                            False,

                        "error":
                            str(error)
                    },
                    400
                )

            return


        json_response(
            self,
            {
                "error":
                    "Endpoint not found."
            },
            404
        )


if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "       KHOTLA TESTNET API"
    )

    print(
        "================================"
    )

    print()

    print(
        "Khotla Coin (KHT)"
    )

    print(
        "Network: Khotla Testnet"
    )

    print(
        "Explorer: /explorer"
    )

    print(
        "Port:",
        PORT
    )

    print()

    server = ThreadingHTTPServer(
        (HOST, PORT),
        KhotlaAPI
    )

    print(
        "Khotla API is running."
    )

    server.serve_forever()
