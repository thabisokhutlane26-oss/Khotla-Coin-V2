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
    print("Amount:", transaction.amount, "KHT")
    print()

    if not transaction.is_valid():

        raise ValueError(
            "Transaction signature is invalid."
        )

    blockchain.add_transaction(
        sender=sender_wallet.address,
        receiver=receiver_wallet.address,
        amount=transaction.amount,
        transaction_id=transaction.transaction_id,
        signature=transaction.signature,
        public_key=transaction.public_key,
        timestamp=transaction.timestamp
    )

    print("Transaction signed.")
    print()

    block = blockchain.mine()

    print("Block mined.")
    print("Block:", block.index)
    print("Hash:", block.hash)
    print()

    print(
        "Blockchain valid:",
        blockchain.is_valid()
    )

    print()

    print("================================")
    print("       KHOTLA TESTNET OK")
    print("================================")


if __name__ == "__main__":

    main()
