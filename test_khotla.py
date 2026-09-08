from khotla_chain import KhotlaChain
from khotla_wallet import KhotlaWallet
from khotla_transaction import KhotlaTransaction


def test_wallet_creation():
    wallet = KhotlaWallet()

    assert wallet.address.startswith("KHT")
    assert len(wallet.address) == 43


def test_transaction_creation():
    wallet1 = KhotlaWallet()
    wallet2 = KhotlaWallet()

    transaction = KhotlaTransaction(
        wallet1.address,
        wallet2.address,
        100
    )

    assert transaction.amount == 100
    assert transaction.sender == wallet1.address
    assert transaction.receiver == wallet2.address


def test_blockchain_mining():
    blockchain = KhotlaChain()

    blockchain.add_transaction(
        "KHT_GENESIS",
        "THABISO_WALLET",
        1000
    )

    block = blockchain.mine()

    assert block is not None
    assert block.index == 1
    assert blockchain.is_valid()


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


if __name__ == "__main__":
    test_wallet_creation()
    test_transaction_creation()
    test_blockchain_mining()
    test_invalid_amount()

    print("================================")
    print("     KHOTLA TESTS PASSED")
    print("================================")
