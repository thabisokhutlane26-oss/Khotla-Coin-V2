from khotla_chain import KhotlaChain
from khotla_wallet import KhotlaWallet
from khotla_transaction import KhotlaTransaction


def main():
    print("================================")
    print("       KHOTLA CHAIN TESTNET")
    print("================================")
    print()

    # Create two wallets
    sender = KhotlaWallet()
    receiver = KhotlaWallet()

    print("Sender wallet:")
    print(sender.address)
    print()

    print("Receiver wallet:")
    print(receiver.address)
    print()

    # Create blockchain
    blockchain = KhotlaChain()

    print("Blockchain started.")
    print()

    # Create a test transaction
    transaction = KhotlaTransaction(
        sender.address,
        receiver.address,
        100
    )

    # Sign the transaction
    transaction.signature = sender.sign_message(
        transaction.transaction_hash()
    )

    # Add transaction to blockchain
    blockchain.add_transaction(
        transaction.sender,
        transaction.receiver,
        transaction.amount
    )

    print("Transaction created.")
    print("Amount:", transaction.amount, "KHT")
    print()

    # Mine the transaction
    block = blockchain.mine()

    if block:
        print("Block mined successfully!")
        print("Block number:", block.index)
        print("Block hash:", block.hash)
    else:
        print("No transactions to mine.")

    print()

    # Verify blockchain
    if blockchain.is_valid():
        print("Blockchain status: VALID")
    else:
        print("Blockchain status: INVALID")

    print()
    print("Khotla Testnet is running.")


if __name__ == "__main__":
    main()
