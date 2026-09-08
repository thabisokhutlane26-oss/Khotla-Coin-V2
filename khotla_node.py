from khotla_wallet import KhotlaWallet
from khotla_transaction import KhotlaTransaction
from khotla_chain import KhotlaChain


def main():

    print("================================")
    print("       KHOTLA CHAIN TESTNET")
    print("================================")
    print()

    sender_wallet = KhotlaWallet()
    receiver_wallet = KhotlaWallet()

    print("Sender wallet:")
    print(sender_wallet.address)
    print()

    print("Receiver wallet:")
    print(receiver_wallet.address)
    print()

    blockchain = KhotlaChain()

    print("Blockchain started.")
    print()

    # --------------------------------
    # FUND SENDER FROM TESTNET GENESIS
    # --------------------------------

    blockchain.add_transaction(
        sender="KHT_GENESIS",
        receiver=sender_wallet.address,
        amount=200
    )

    faucet_block = blockchain.mine()

    if faucet_block is None:

        raise ValueError(
            "Failed to fund sender wallet."
        )

    print("Sender funded.")
    print(
        "Sender balance:",
        blockchain.get_balance(
            sender_wallet.address
        ),
        "KHT"
    )
    print()

    # --------------------------------
    # CREATE SIGNED TRANSACTION
    # --------------------------------

    transaction = KhotlaTransaction(
        sender_wallet.address,
        receiver_wallet.address,
        100
    )

    signature = sender_wallet.sign_message(
        transaction.transaction_hash()
    )

    transaction.signature = signature
    transaction.public_key = sender_wallet.public_key

    print("Transaction created.")
    print(
        "Amount:",
        transaction.amount,
        "KHT"
    )
    print()

    # --------------------------------
    # VERIFY TRANSACTION
    # --------------------------------

    if not transaction.is_valid():

        raise ValueError(
            "Transaction signature is invalid."
        )

    print("Transaction signature: VALID")
    print()

    # --------------------------------
    # ADD TRANSACTION
    # --------------------------------

    blockchain.add_transaction(
        sender=sender_wallet.address,
        receiver=receiver_wallet.address,
        amount=transaction.amount,
        transaction_id=transaction.transaction_id,
        signature=transaction.signature,
        public_key=transaction.public_key,
        timestamp=transaction.timestamp
    )

    print("Transaction added.")
    print()

    # --------------------------------
    # MINE TRANSACTION
    # --------------------------------

    block = blockchain.mine()

    if block is None:

        raise ValueError(
            "Transaction was not mined."
        )

    print("Block mined.")
    print(
        "Block:",
        block.index
    )

    print(
        "Hash:",
        block.hash
    )

    print()

    # --------------------------------
    # FINAL BALANCES
    # --------------------------------

    sender_balance = (
        blockchain.get_balance(
            sender_wallet.address
        )
    )

    receiver_balance = (
        blockchain.get_balance(
            receiver_wallet.address
        )
    )

    print("Final balances:")
    print(
        "Sender:",
        sender_balance,
        "KHT"
    )

    print(
        "Receiver:",
        receiver_balance,
        "KHT"
    )

    print()

    # --------------------------------
    # VALIDATE BLOCKCHAIN
    # --------------------------------

    chain_valid = (
        blockchain.is_valid()
    )

    print(
        "Blockchain valid:",
        chain_valid
    )

    print()

    if not chain_valid:

        raise ValueError(
            "Blockchain validation failed."
        )

    if sender_balance != 100:

        raise ValueError(
            "Sender balance is incorrect."
        )

    if receiver_balance != 100:

        raise ValueError(
            "Receiver balance is incorrect."
        )

    print("================================")
    print("       KHOTLA TESTNET OK")
    print("================================")


if __name__ == "__main__":

    main()
