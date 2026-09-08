import os

from khotla_wallet import KhotlaWallet
from khotla_transaction import KhotlaTransaction
from khotla_chain import KhotlaChain


TEST_CHAIN_FILE = "test_khotla_chain_data.json"


def test_wallet_creation():

    wallet = KhotlaWallet()

    assert wallet.address.startswith("KHT")
    assert len(wallet.address) == 43

    assert len(wallet.private_key) == 64
    assert len(wallet.public_key) == 64

    print("Wallet creation: OK")


def test_wallet_signature():

    wallet = KhotlaWallet()

    message = "Khotla Testnet Test"

    signature = wallet.sign_message(
        message
    )

    assert wallet.verify_signature(
        message,
        signature
    )

    assert KhotlaWallet.verify_external_signature(
        message,
        signature,
        wallet.public_key
    )

    print("Wallet signature: OK")


def test_transaction_signature():

    sender = KhotlaWallet()
    receiver = KhotlaWallet()

    transaction = KhotlaTransaction(
        sender.address,
        receiver.address,
        25
    )

    signature = sender.sign_message(
        transaction.transaction_hash()
    )

    transaction.signature = signature
    transaction.public_key = sender.public_key

    assert transaction.is_valid()

    print("Transaction signature: OK")


def test_invalid_transaction():

    sender = KhotlaWallet()
    receiver = KhotlaWallet()

    transaction = KhotlaTransaction(
        sender.address,
        receiver.address,
        25
    )

    signature = sender.sign_message(
        transaction.transaction_hash()
    )

    transaction.signature = signature
    transaction.public_key = sender.public_key

    assert transaction.is_valid()

    transaction.amount = 1000

    assert not transaction.is_valid()

    print("Invalid transaction protection: OK")


def test_blockchain_genesis():

    blockchain = KhotlaChain(
        storage_file=TEST_CHAIN_FILE
    )

    assert len(blockchain.chain) >= 1
    assert blockchain.chain[0].index == 0
    assert blockchain.chain[0].previous_hash == "0"

    print("Blockchain genesis: OK")


def test_blockchain_mining():

    blockchain = KhotlaChain(
        storage_file=TEST_CHAIN_FILE
    )

    sender = KhotlaWallet()
    receiver = KhotlaWallet()

    # Fund sender from the trusted testnet genesis account.

    blockchain.add_transaction(
        sender="KHT_GENESIS",
        receiver=sender.address,
        amount=100
    )

    faucet_block = blockchain.mine()

    assert faucet_block is not None

    assert blockchain.get_balance(
        sender.address
    ) == 100

    print("Testnet funding: OK")

    # Create a real signed transaction.

    transaction = KhotlaTransaction(
        sender.address,
        receiver.address,
        25
    )

    transaction.signature = (
        sender.sign_message(
            transaction.transaction_hash()
        )
    )

    transaction.public_key = (
        sender.public_key
    )

    assert transaction.is_valid()

    # Add the signed transaction.

    blockchain.add_transaction(
        sender=sender.address,
        receiver=receiver.address,
        amount=25,
        transaction_id=transaction.transaction_id,
        signature=transaction.signature,
        public_key=transaction.public_key,
        timestamp=transaction.timestamp
    )

    assert len(
        blockchain.pending_transactions
    ) == 1

    # Mine the transfer.

    transfer_block = blockchain.mine()

    assert transfer_block is not None

    # Check final balances.

    assert blockchain.get_balance(
        sender.address
    ) == 75

    assert blockchain.get_balance(
        receiver.address
    ) == 25

    assert blockchain.is_valid()

    print("Blockchain mining: OK")


def test_insufficient_balance():

    blockchain = KhotlaChain(
        storage_file=TEST_CHAIN_FILE
    )

    sender = KhotlaWallet()
    receiver = KhotlaWallet()

    try:

        blockchain.add_transaction(
            sender=sender.address,
            receiver=receiver.address,
            amount=1,
            signature="invalid",
            public_key=sender.public_key
        )

        raise AssertionError(
            "Insufficient balance was not blocked."
        )

    except ValueError as error:

        assert str(error) == (
            "Insufficient balance."
        )

    print("Insufficient balance protection: OK")


def test_chain_tamper_detection():

    blockchain = KhotlaChain(
        storage_file=TEST_CHAIN_FILE
    )

    sender = KhotlaWallet()
    receiver = KhotlaWallet()

    # Fund sender.

    blockchain.add_transaction(
        sender="KHT_GENESIS",
        receiver=sender.address,
        amount=50
    )

    blockchain.mine()

    # Create valid signed transaction.

    transaction = KhotlaTransaction(
        sender.address,
        receiver.address,
        10
    )

    transaction.signature = (
        sender.sign_message(
            transaction.transaction_hash()
        )
    )

    transaction.public_key = (
        sender.public_key
    )

    blockchain.add_transaction(
        sender=sender.address,
        receiver=receiver.address,
        amount=10,
        transaction_id=transaction.transaction_id,
        signature=transaction.signature,
        public_key=transaction.public_key,
        timestamp=transaction.timestamp
    )

    blockchain.mine()

    assert blockchain.is_valid()

    # Tamper with a confirmed transaction.

    blockchain.chain[1].transactions[0][
        "amount"
    ] = 999

    assert not blockchain.is_valid()

    print("Chain tamper detection: OK")


def cleanup():

    if os.path.exists(
        TEST_CHAIN_FILE
    ):

        os.remove(
            TEST_CHAIN_FILE
        )


def main():

    print("================================")
    print("       KHOTLA COIN TESTS")
    print("================================")
    print()

    cleanup()

    test_wallet_creation()

    cleanup()

    test_wallet_signature()

    cleanup()

    test_transaction_signature()

    cleanup()

    test_invalid_transaction()

    cleanup()

    test_blockchain_genesis()

    cleanup()

    test_blockchain_mining()

    cleanup()

    test_insufficient_balance()

    cleanup()

    test_chain_tamper_detection()

    cleanup()

    print()
    print("================================")
    print("       ALL KHOTLA TESTS OK")
    print("================================")


if __name__ == "__main__":

    main()
