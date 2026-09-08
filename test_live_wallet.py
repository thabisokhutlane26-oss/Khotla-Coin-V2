from khotla_wallet import KhotlaWallet
from khotla_transaction import KhotlaTransaction
from khotla_chain import KhotlaChain


def main():

    print("================================")
    print("     KHOTLA LIVE WALLET TEST")
    print("================================")
    print()

    # Create two real Ed25519 wallets

    sender = KhotlaWallet()
    receiver = KhotlaWallet()

    print("Sender address:")
    print(sender.address)
    print()

    print("Receiver address:")
    print(receiver.address)
    print()

    # Create a blockchain

    blockchain = KhotlaChain()

    print("Blockchain loaded.")
    print(
        "Sender balance:",
        blockchain.get_balance(
            sender.address
        ),
        "KHT"
    )
    print()

    # Give the sender testnet KHT

    faucet_transaction = (
        blockchain.add_transaction(
            sender="KHT_GENESIS",
            receiver=sender.address,
            amount=100
        )
    )

    blockchain.mine()

    print("Faucet transaction confirmed.")
    print(
        "Sender balance:",
        blockchain.get_balance(
            sender.address
        ),
        "KHT"
    )
    print()

    # Create a real signed transaction

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

    print("Transaction created.")
    print("Amount:", transaction.amount, "KHT")
    print()

    # Verify signature

    if not transaction.is_valid():

        raise ValueError(
            "Transaction signature verification failed."
        )

    print("Signature verification: OK")
    print()

    # Add transaction to blockchain

    blockchain.add_transaction(
        sender=sender.address,
        receiver=receiver.address,
        amount=transaction.amount,
        transaction_id=transaction.transaction_id,
        signature=transaction.signature,
        public_key=transaction.public_key,
        timestamp=transaction.timestamp
    )

    print("Transaction added to pending pool.")
    print()

    # Mine transaction

    block = blockchain.mine()

    if block is None:

        raise ValueError(
            "Transaction was not mined."
        )

    print("Transaction mined.")
    print("Block:", block.index)
    print("Block hash:", block.hash)
    print()

    # Check balances

    sender_balance = blockchain.get_balance(
        sender.address
    )

    receiver_balance = blockchain.get_balance(
        receiver.address
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

    # Validate blockchain

    valid = blockchain.is_valid()

    print(
        "Blockchain valid:",
        valid
    )

    print()

    if not valid:

        raise ValueError(
            "Blockchain validation failed."
        )

    if receiver_balance != 25:

        raise ValueError(
            "Receiver balance is incorrect."
        )

    if sender_balance != 75:

        raise ValueError(
            "Sender balance is incorrect."
        )

    print("================================")
    print("       KHOTLA WALLET TEST OK")
    print("================================")


if __name__ == "__main__":

    main()
