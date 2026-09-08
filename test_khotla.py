import os
import tempfile

from khotla_chain import KhotlaChain
from khotla_wallet import KhotlaWallet
from khotla_transaction import KhotlaTransaction


def test_wallet_creation():

    wallet = KhotlaWallet()

    assert wallet.address.startswith(
        "KHT"
    )

    assert len(
        wallet.address
    ) == 43


def test_transaction_creation():

    wallet1 = KhotlaWallet()
    wallet2 = KhotlaWallet()

    transaction = KhotlaTransaction(
        wallet1.address,
        wallet2.address,
        100
    )

    assert transaction.amount == 100

    assert transaction.sender == (
        wallet1.address
    )

    assert transaction.receiver == (
        wallet2.address
    )

    assert transaction.transaction_id

    assert len(
        transaction.transaction_hash()
    ) == 64


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

        blockchain = KhotlaChain(
            storage_file=chain_file
        )

        blockchain.add_transaction(
            "KHT_GENESIS",
            "THABISO_WALLET",
            1000
        )

        block = blockchain.mine()

        assert block is not None

        assert block.index == 1

        assert blockchain.is_valid()

        assert os.path.exists(
            chain_file
        )


def test_blockchain_persistence():

    with tempfile.TemporaryDirectory() as folder:

        chain_file = os.path.join(
            folder,
            "chain.json"
        )

        blockchain1 = KhotlaChain(
            storage_file=chain_file
        )

        blockchain1.add_transaction(
            "KHT_GENESIS",
            "THABISO_WALLET",
            500
        )

        blockchain1.mine()

        blockchain2 = KhotlaChain(
            storage_file=chain_file
        )

        assert len(
            blockchain2.chain
        ) == len(
            blockchain1.chain
        )

        assert blockchain2.is_valid()


if __name__ == "__main__":

    test_wallet_creation()

    test_transaction_creation()

    test_genesis_transaction()

    test_invalid_amount()

    test_blockchain_mining()

    test_blockchain_persistence()

    print(
        "================================"
    )

    print(
        "   KHOTLA STEP 10A TESTS PASSED"
    )

    print(
        "================================"
    )
