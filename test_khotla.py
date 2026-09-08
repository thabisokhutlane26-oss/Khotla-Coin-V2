import os
import tempfile

from khotla_chain import KhotlaChain
from khotla_wallet import KhotlaWallet
from khotla_transaction import KhotlaTransaction


def test_wallet_creation():

    wallet = KhotlaWallet()

    assert wallet.address.startswith("KHT")
    assert len(wallet.address) == 43

    assert len(wallet.private_key) == 64
    assert len(wallet.public_key) == 64


def test_ed25519_signature():

    wallet = KhotlaWallet()

    message = "Khotla Testnet Transaction"

    signature = wallet.sign_message(message)

    assert signature

    assert wallet.verify_signature(
        message,
        signature
    )

    assert KhotlaWallet.verify_external_signature(
        message,
        signature,
        wallet.public_key
    )

    assert not wallet.verify_signature(
        "Wrong message",
        signature
    )


def test_transaction_creation():

    wallet1 = KhotlaWallet()
    wallet2 = KhotlaWallet()

    transaction = KhotlaTransaction(
        wallet1.address,
        wallet2.address,
        100
    )

    signature = wallet1.sign_message(
        transaction.transaction_hash()
    )

    transaction.signature = signature
    transaction.public_key = wallet1.public_key

    assert transaction.amount == 100
    assert transaction.sender == wallet1.address
    assert transaction.receiver == wallet2.address
    assert transaction.transaction_id
    assert transaction.timestamp is not None
    assert len(transaction.transaction_hash()) == 64
    assert transaction.is_valid()


def test_genesis_transaction():

    transaction = KhotlaTransaction(
        "KHT_GENESIS",
        "THABISO_WALLET",
        1000
    )

    assert transaction.is_valid()


def test_invalid_amount():

    wallet = KhotlaWallet()

    try:

        KhotlaTransaction(
            wallet.address,
            "KHT_RECEIVER",
            -10
        )

        assert False

    except ValueError:

        assert True


def test_blockchain_mining():

    with tempfile.TemporaryDirectory() as folder:

        chain_file = os.path.join(
            folder,
            "chain.json"
        )

        sender = KhotlaWallet()
        receiver = KhotlaWallet()

        blockchain = KhotlaChain(
            storage_file=chain_file
        )

        transaction = KhotlaTransaction(
            sender.address,
            receiver.address,
            100
        )

        signature = sender.sign_message(
            transaction.transaction_hash()
        )

        transaction.signature = signature
        transaction.public_key = sender.public_key

        blockchain.add_transaction(
            sender=sender.address,
            receiver=receiver.address,
            amount=transaction.amount,
            transaction_id=transaction.transaction_id,
            signature=transaction.signature,
            public_key=transaction.public_key,
            timestamp=transaction.timestamp
        )

        block = blockchain.mine()

        assert block is not None
        assert block.index == 1
        assert blockchain.is_valid()
        assert os.path.exists(chain_file)


def test_blockchain_persistence():

    with tempfile.TemporaryDirectory() as folder:

        chain_file = os.path.join(
            folder,
            "chain.json"
        )

        sender = KhotlaWallet()
        receiver = KhotlaWallet()

        blockchain1 = KhotlaChain(
            storage_file=chain_file
        )

        transaction = KhotlaTransaction(
            sender.address,
            receiver.address,
            50
        )

        signature = sender.sign_message(
            transaction.transaction_hash()
        )

        transaction.signature = signature
        transaction.public_key = sender.public_key

        blockchain1.add_transaction(
            sender=sender.address,
            receiver=receiver.address,
            amount=transaction.amount,
            transaction_id=transaction.transaction_id,
            signature=transaction.signature,
            public_key=transaction.public_key,
            timestamp=transaction.timestamp
        )

        block = blockchain1.mine()

        assert block is not None
        assert blockchain1.is_valid()

        blockchain2 = KhotlaChain(
            storage_file=chain_file
        )

        assert len(blockchain2.chain) == len(
            blockchain1.chain
        )

        assert blockchain2.is_valid()


def test_tampered_transaction_fails():

    sender = KhotlaWallet()
    receiver = KhotlaWallet()

    blockchain = KhotlaChain(
        storage_file=os.path.join(
            tempfile.gettempdir(),
            "khotla_tamper_test.json"
        )
    )

    transaction = KhotlaTransaction(
        sender.address,
        receiver.address,
        100
    )

    signature = sender.sign_message(
        transaction.transaction_hash()
    )

    transaction.signature = signature
    transaction.public_key = sender.public_key

    blockchain.add_transaction(
        sender=sender.address,
        receiver=receiver.address,
        amount=transaction.amount,
        transaction_id=transaction.transaction_id,
        signature=transaction.signature,
        public_key=transaction.public_key,
        timestamp=transaction.timestamp
    )

    # Tamper with the amount after signing.
    blockchain.pending_transactions[0]["amount"] = 999

    assert not blockchain.validate_transaction(
        blockchain.pending_transactions[0]
    )


if __name__ == "__main__":

    test_wallet_creation()

    test_ed25519_signature()

    test_transaction_creation()

    test_genesis_transaction()

    test_invalid_amount()

    test_blockchain_mining()

    test_blockchain_persistence()

    test_tampered_transaction_fails()

    print()
    print("================================")
    print("   KHOTLA STEP 10B TESTS PASSED")
    print("================================")
