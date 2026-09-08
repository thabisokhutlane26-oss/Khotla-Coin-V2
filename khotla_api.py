import hashlib
import html
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


def format_timestamp(timestamp):

    try:

        return time.strftime(
            "%Y-%m-%d %H:%M:%S UTC",
            time.gmtime(float(timestamp))
        )

    except Exception:

        return "Unknown"


def short_hash(value, length=18):

    if not value:
        return "N/A"

    value = str(value)

    if len(value) <= length:
        return value

    return (
        value[:length // 2]
        + "..."
        + value[-length // 2:]
    )


def explorer_page():

    latest_block = blockchain.latest_block()

    total_transactions = 0

    for block in blockchain.chain:

        total_transactions += len(
            block.transactions
        )

    recent_blocks = []

    for block in reversed(
        blockchain.chain[-12:]
    ):

        recent_blocks.append({
            "index": block.index,
            "timestamp": format_timestamp(
                block.timestamp
            ),
            "transactions": len(
                block.transactions
            ),
            "hash": block.hash,
            "previous_hash": block.previous_hash
        })

    blocks_html = ""

    for block in recent_blocks:

        blocks_html += f"""
        <div class="block">

            <div class="block-top">

                <span class="block-number">
                    Block #{html.escape(str(block["index"]))}
                </span>

                <span class="status">
                    CONFIRMED
                </span>

            </div>

            <div class="block-row">
                <span>Transactions</span>
                <strong>
                    {html.escape(str(block["transactions"]))}
                </strong>
            </div>

            <div class="block-row">
                <span>Time</span>
                <strong>
                    {html.escape(block["timestamp"])}
                </strong>
            </div>

            <div class="hash">
                <span>Hash</span>
                <code>
                    {html.escape(short_hash(block["hash"], 30))}
                </code>
            </div>

        </div>
        """

    if not blocks_html:

        blocks_html = """
        <div class="empty">
            No blocks available yet.
        </div>
        """

    page = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Khotla Block Explorer</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        #07110b;

    color:
        #ffffff;
}}

.header {{

    padding:
        24px 18px;

    background:
        linear-gradient(
            135deg,
            #0c2515,
            #07110b
        );

    border-bottom:
        1px solid #173a22;
}}

.logo {{

    font-size:
        28px;

    font-weight:
        900;

    letter-spacing:
        1px;
}}

.logo span {{

    color:
        #39ff88;
}}

.subtitle {{

    margin-top:
        6px;

    color:
        #91a99a;

    font-size:
        14px;
}}

.online {{

    display:
        inline-block;

    margin-top:
        14px;

    padding:
        7px 12px;

    border-radius:
        20px;

    background:
        #123a20;

    color:
        #39ff88;

    font-size:
        12px;

    font-weight:
        800;
}}

.container {{

    max-width:
        1100px;

    margin:
        auto;

    padding:
        20px;
}}

.search {{

    display:
        flex;

    gap:
        10px;

    margin-bottom:
        22px;
}}

.search input {{

    flex:
        1;

    min-width:
        0;

    padding:
        14px;

    border:
        1px solid #244b30;

    border-radius:
        10px;

    background:
        #0d1d13;

    color:
        white;

    outline:
        none;

    font-size:
        14px;
}}

.search button {{

    padding:
        14px 18px;

    border:
        none;

    border-radius:
        10px;

    background:
        #39ff88;

    color:
        #06100a;

    font-weight:
        900;

    cursor:
        pointer;
}}

.stats {{

    display:
        grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(
                150px,
                1fr
            )
        );

    gap:
        12px;

    margin-bottom:
        25px;
}}

.card {{

    padding:
        18px;

    background:
        #0d1d13;

    border:
        1px solid #173a22;

    border-radius:
        14px;
}}

.card-title {{

    color:
        #7f9988;

    font-size:
        12px;

    text-transform:
        uppercase;

    letter-spacing:
        1px;
}}

.card-value {{

    margin-top:
        8px;

    font-size:
        22px;

    font-weight:
        900;

    word-break:
        break-word;
}}

.section-title {{

    margin:
        25px 0 12px;

    font-size:
        20px;

    font-weight:
        900;
}}

.block {{

    margin-bottom:
        12px;

    padding:
        17px;

    background:
        #0d1d13;

    border:
        1px solid #173a22;

    border-radius:
        14px;
}}

.block-top {{

    display:
        flex;

    justify-content:
        space-between;

    align-items:
        center;

    gap:
        10px;

    margin-bottom:
        14px;
}}

.block-number {{

    font-size:
        17px;

    font-weight:
        900;
}}

.status {{

    padding:
        5px 9px;

    border-radius:
        20px;

    background:
        #123a20;

    color:
        #39ff88;

    font-size:
        10px;

    font-weight:
        900;
}}

.block-row {{

    display:
        flex;

    justify-content:
        space-between;

    gap:
        15px;

    padding:
        8px 0;

    color:
        #8fa697;

    font-size:
        13px;
}}

.block-row strong {{

    color:
        #ffffff;

    text-align:
        right;
}}

.hash {{

    margin-top:
        10px;

    padding-top:
        10px;

    border-top:
        1px solid #173a22;

}}

.hash span {{

    display:
        block;

    color:
        #8fa697;

    font-size:
        12px;

    margin-bottom:
        6px;
}}

code {{

    color:
        #39ff88;

    font-size:
        12px;

    word-break:
        break-all;
}}

.footer {{

    padding:
        30px 20px;

    text-align:
        center;

    color:
        #65786c;

    font-size:
        12px;
}}

.empty {{

    padding:
        30px;

    text-align:
        center;

    color:
        #7f9988;
}}

@media (max-width: 500px) {{

    .search {{

        flex-direction:
            column;
    }}

    .search button {{

        width:
            100%;
    }}

    .block-row {{

        flex-direction:
            column;

        gap:
            3px;
    }}

    .block-row strong {{

        text-align:
            left;
    }}

}}

</style>

</head>

<body>

<div class="header">

    <div class="logo">
        KHOTLA <span>EXPLORER</span>
    </div>

    <div class="subtitle">
        Khotla Coin Blockchain Explorer
    </div>

    <div class="online">
        ● TESTNET ONLINE
    </div>

</div>

<div class="container">

    <div class="search">

        <input
            id="searchInput"
            type="text"
            placeholder="Search transaction ID..."
        >

        <button onclick="searchTransaction()">
            SEARCH
        </button>

    </div>

    <div id="searchResult"></div>

    <div class="stats">

        <div class="card">

            <div class="card-title">
                Network
            </div>

            <div class="card-value">
                Testnet
            </div>

        </div>

        <div class="card">

            <div class="card-title">
                Coin
            </div>

            <div class="card-value">
                KHT
            </div>

        </div>

        <div class="card">

            <div class="card-title">
                Blocks
            </div>

            <div class="card-value">
                {len(blockchain.chain)}
            </div>

        </div>

        <div class="card">

            <div class="card-title">
                Transactions
            </div>

            <div class="card-value">
                {total_transactions}
            </div>

        </div>

        <div class="card">

            <div class="card-title">
                Pending
            </div>

            <div class="card-value">
                {len(blockchain.pending_transactions)}
            </div>

        </div>

        <div class="card">

            <div class="card-title">
                Chain
            </div>

            <div class="card-value">
                {"VALID" if blockchain.is_valid() else "INVALID"}
            </div>

        </div>

    </div>

    <div class="section-title">
        Latest Block
    </div>

    <div class="block">

        <div class="block-top">

            <span class="block-number">
                Block #{latest_block.index}
            </span>

            <span class="status">
                CONFIRMED
            </span>

        </div>

        <div class="block-row">
            <span>Transactions</span>
            <strong>
                {len(latest_block.transactions)}
            </strong>
        </div>

        <div class="block-row">
            <span>Nonce</span>
            <strong>
                {latest_block.nonce}
            </strong>
        </div>

        <div class="block-row">
            <span>Time</span>
            <strong>
                {html.escape(
                    format_timestamp(
                        latest_block.timestamp
                    )
                )}
            </strong>
        </div>

        <div class="hash">

            <span>
                Block Hash
            </span>

            <code>
                {html.escape(latest_block.hash)}
            </code>

        </div>

    </div>

    <div class="section-title">
        Recent Blocks
    </div>

    {blocks_html}

</div>

<div class="footer">

    Khotla Coin • KHT • Khotla Testnet

    <br><br>

    Blockchain Explorer v1.0

</div>

<script>

async function searchTransaction() {{

    const input =
        document.getElementById(
            "searchInput"
        );

    const result =
        document.getElementById(
            "searchResult"
        );

    const id =
        input.value.trim();

    if (!id) {{

        result.innerHTML = "";

        return;
    }}

    result.innerHTML =
        '<div class="block">Searching...</div>';

    try {{

        const response =
            await fetch(
                "/transaction?id="
                + encodeURIComponent(id)
            );

        const data =
            await response.json();

        if (!response.ok) {{

            result.innerHTML =
                '<div class="block">'
                + '<strong>Transaction not found.</strong>'
                + '</div>';

            return;
        }}

        const transaction =
            data.transaction;

        result.innerHTML =
            '<div class="block">'
            + '<div class="block-top">'
            + '<span class="block-number">'
            + 'Transaction Found'
            + '</span>'
            + '<span class="status">'
            + data.status.toUpperCase()
            + '</span>'
            + '</div>'
            + '<div class="block-row">'
            + '<span>Amount</span>'
            + '<strong>'
            + transaction.amount
            + ' KHT'
            + '</strong>'
            + '</div>'
            + '<div class="block-row">'
            + '<span>Sender</span>'
            + '<strong>'
            + transaction.sender
            + '</strong>'
            + '</div>'
            + '<div class="block-row">'
            + '<span>Receiver</span>'
            + '<strong>'
            + transaction.receiver
            + '</strong>'
            + '</div>'
            + '</div>';

    }} catch (error) {{

        result.innerHTML =
            '<div class="block">'
            + '<strong>Search error.</strong>'
            + '</div>';

    }}

}}

</script>

</body>

</html>
"""

    return page


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

    def send_html(
        self,
        page,
        status=200
    ):

        response = page.encode(
            "utf-8"
        )

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
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

        parsed = urlparse(
            self.path
        )

        path = parsed.path

        if path == "/":

            self.send_json({
                "name": "Khotla Testnet API",
                "coin": "Khotla Coin",
                "ticker": "KHT",
                "network": "Khotla Testnet",
                "status": "online",
                "version": "2.2"
            })

            return

        if path == "/explorer":

            self.send_html(
                explorer_page()
            )

            return

        if path == "/status":

            self.send_json({

                "network":
                    "Khotla Testnet",

                "coin":
                    "Khotla Coin",

                "ticker":
                    "KHT",

                "status":
                    "online",

                "blocks":
                    len(blockchain.chain),

                "pending_transactions":
                    len(
                        blockchain.pending_transactions
                    ),

                "latest_block":
                    blockchain.latest_block().hash,

                "chain_valid":
                    blockchain.is_valid()

            })

            return

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
                    "error":
                        "Address is required."
                }, 400)

                return

            if not valid_address(address):

                self.send_json({
                    "error":
                        "Invalid KHT address."
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

                "address":
                    address,

                "balance":
                    balance,

                "available_balance":
                    available_balance,

                "currency":
                    "KHT",

                "network":
                    "Khotla Testnet"

            })

            return

        if path == "/chain":

            chain_data = []

            for block in blockchain.chain:

                chain_data.append(
                    block_to_dict(block)
                )

            self.send_json({

                "chain":
                    chain_data,

                "length":
                    len(chain_data),

                "valid":
                    blockchain.is_valid()

            })

            return

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
                    "error":
                        "Transaction ID is required."
                }, 400)

                return

            for block in blockchain.chain:

                for transaction in block.transactions:

                    if (
                        transaction.get(
                            "transaction_id"
                        )
                        == transaction_id
                    ):

                        self.send_json({

                            "transaction":
                                transaction,

                            "block":
                                block.index,

                            "block_hash":
                                block.hash,

                            "status":
                                "confirmed"

                        })

                        return

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

                        "transaction":
                            transaction,

                        "status":
                            "pending"

                    })

                    return

            self.send_json({
                "error":
                    "Transaction not found."
            }, 404)

            return

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
                    "error":
                        "Address is required."
                }, 400)

                return

            if not valid_address(address):

                self.send_json({
                    "error":
                        "Invalid KHT address."
                }, 400)

                return

            transactions = []

            for block in blockchain.chain:

                for transaction in block.transactions:

                    if (
                        transaction.get(
                            "sender"
                        )
                        == address
                        or
                        transaction.get(
                            "receiver"
                        )
                        == address
                    ):

                        transactions.append({

                            "transaction":
                                transaction,

                            "block":
                                block.index,

                            "block_hash":
                                block.hash,

                            "status":
                                "confirmed"

                        })

            for transaction in (
                blockchain.pending_transactions
            ):

                if (
                    transaction.get(
                        "sender"
                    )
                    == address
                    or
                    transaction.get(
                        "receiver"
                    )
                    == address
                ):

                    transactions.append({

                        "transaction":
                            transaction,

                        "status":
                            "pending"

                    })

            self.send_json({

                "address":
                    address,

                "transactions":
                    transactions,

                "count":
                    len(transactions),

                "network":
                    "Khotla Testnet"

            })

            return

        self.send_json({

            "error":
                "Endpoint not found."

        }, 404)

    def do_POST(self):

        parsed = urlparse(
            self.path
        )

        path = parsed.path

        try:

            data = self.read_json()

        except Exception:

            self.send_json({
                "error":
                    "Invalid JSON."
            }, 400)

            return

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
                    "error":
                        "Sender and receiver are required."
                }, 400)

                return

            if not valid_address(sender):

                self.send_json({
                    "error":
                        "Invalid sender KHT address."
                }, 400)

                return

            if not valid_address(receiver):

                self.send_json({
                    "error":
                        "Invalid receiver KHT address."
                }, 400)

                return

            try:

                amount = float(amount)

            except (
                TypeError,
                ValueError
            ):

                self.send_json({
                    "error":
                        "Amount must be a number."
                }, 400)

                return

            if amount <= 0:

                self.send_json({
                    "error":
                        "Amount must be greater than zero."
                }, 400)

                return

            available_balance = (
                blockchain.get_available_balance(
                    sender
                )
            )

            if amount > available_balance:

                self.send_json({

                    "error":
                        "Insufficient KHT balance.",

                    "balance":
                        blockchain.get_balance(
                            sender
                        ),

                    "available_balance":
                        available_balance

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

                        transaction_id=
                            transaction_id,

                        signature=signature,

                        public_key=public_key
                    )
                )

            except ValueError as error:

                self.send_json({
                    "error":
                        str(error)
                }, 400)

                return

            self.send_json({

                "message":
                    "Transaction added.",

                "transaction_id":
                    transaction[
                        "transaction_id"
                    ],

                "sender":
                    sender,

                "receiver":
                    receiver,

                "amount":
                    amount,

                "currency":
                    "KHT",

                "signature":
                    signature,

                "public_key":
                    public_key,

                "status":
                    "pending",

                "network":
                    "Khotla Testnet"

            })

            return

        if path == "/mine":

            try:

                block = blockchain.mine()

            except ValueError as error:

                self.send_json({
                    "error":
                        str(error)
                }, 400)

                return

            if block is None:

                self.send_json({

                    "message":
                        "No pending transactions.",

                    "status":
                        "nothing_to_mine"

                })

                return

            self.send_json({

                "message":
                    "Block mined successfully.",

                "block":
                    block_to_dict(block),

                "chain_valid":
                    blockchain.is_valid()

            })

            return

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
                    "error":
                        "Wallet address is required."
                }, 400)

                return

            if not valid_address(address):

                self.send_json({
                    "error":
                        "Invalid KHT wallet address."
                }, 400)

                return

            try:

                amount = float(amount)

            except (
                TypeError,
                ValueError
            ):

                self.send_json({
                    "error":
                        "Amount must be a number."
                }, 400)

                return

            if amount <= 0:

                self.send_json({
                    "error":
                        "Amount must be greater than zero."
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

                    transaction_id=
                        transaction_id,

                    signature=None,

                    public_key=None

                )

                block = blockchain.mine()

            except ValueError as error:

                self.send_json({
                    "error":
                        str(error)
                }, 400)

                return

            self.send_json({

                "message":
                    "Testnet KHT sent.",

                "transaction_id":
                    transaction_id,

                "address":
                    address,

                "amount":
                    amount,

                "currency":
                    "KHT",

                "block":
                    block.index,

                "block_hash":
                    block.hash,

                "network":
                    "Khotla Testnet",

                "status":
                    "confirmed"

            })

            return

        self.send_json({

            "error":
                "Endpoint not found."

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
    print("Version: 2.2")
    print()
    print("Explorer: /explorer")
    print()
    print("API running on port:", port)
    print()
    print("Khotla Testnet API is running!")

    server.serve_forever()


if __name__ == "__main__":

    run_server()
