package com.khotla.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.graphics.Color
import android.view.Gravity
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.security.MessageDigest
import java.util.UUID

class MainActivity : AppCompatActivity() {

    private lateinit var balanceText: TextView
    private lateinit var addressText: TextView
    private lateinit var statusText: TextView
    private lateinit var historyText: TextView

    private var walletAddress: String? = null

    private val preferencesName = "khotla_wallet"
    private val addressKey = "wallet_address"
    private val balanceKey = "wallet_balance"
    private val historyKey = "transaction_history"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        loadWallet()
        showMainScreen()
    }

    private fun loadWallet() {

        val preferences = getSharedPreferences(
            preferencesName,
            Context.MODE_PRIVATE
        )

        walletAddress = preferences.getString(
            addressKey,
            null
        )
    }

    private fun saveWallet(address: String) {

        getSharedPreferences(
            preferencesName,
            Context.MODE_PRIVATE
        )
            .edit()
            .putString(addressKey, address)
            .putFloat(balanceKey, 0f)
            .apply()
    }

    private fun showMainScreen() {

        val layout = createLayout()

        val title = createText(
            "KHOTLA WALLET",
            30f,
            Color.BLACK
        )

        val coin = createText(
            "Khotla Coin (KHT)",
            20f,
            Color.DKGRAY
        )

        val network = createText(
            "🌐 Khotla Testnet",
            16f,
            Color.DKGRAY
        )

        balanceText = createText(
            "",
            25f,
            Color.BLACK
        )

        addressText = createText(
            "",
            14f,
            Color.DKGRAY
        )

        updateWalletDisplay()

        val createButton = Button(this)
        createButton.text = "CREATE WALLET"

        createButton.setOnClickListener {
            createWallet()
        }

        val receiveButton = Button(this)
        receiveButton.text = "RECEIVE KHT"

        receiveButton.setOnClickListener {
            showReceiveScreen()
        }

        val sendButton = Button(this)
        sendButton.text = "SEND KHT"

        sendButton.setOnClickListener {
            showSendScreen()
        }

        val refreshButton = Button(this)
        refreshButton.text = "REFRESH BALANCE"

        refreshButton.setOnClickListener {
            refreshBalance()
        }

        val historyButton = Button(this)
        historyButton.text = "TRANSACTION HISTORY"

        historyButton.setOnClickListener {
            showHistoryScreen()
        }

        statusText = createText(
            "",
            14f,
            Color.DKGRAY
        )

        layout.addView(title)
        layout.addView(coin)
        layout.addView(network)
        layout.addView(balanceText)
        layout.addView(addressText)
        layout.addView(createButton)
        layout.addView(receiveButton)
        layout.addView(sendButton)
        layout.addView(refreshButton)
        layout.addView(historyButton)
        layout.addView(statusText)

        setContentView(layout)
    }

    private fun createWallet() {

        if (walletAddress != null) {

            statusText.text =
                "A wallet already exists on this device."

            return
        }

        val randomId = UUID.randomUUID().toString()

        val hash = MessageDigest
            .getInstance("SHA-256")
            .digest(randomId.toByteArray())
            .joinToString("") {
                "%02x".format(it)
            }

        walletAddress =
            "KHT" + hash.take(40)

        saveWallet(walletAddress!!)

        updateWalletDisplay()

        statusText.text =
            "Wallet created successfully!"
    }

    private fun updateWalletDisplay() {

        if (walletAddress == null) {

            balanceText.text =
                "\nBalance\n0 KHT"

            addressText.text =
                "\nWallet not created yet"

            return
        }

        balanceText.text =
            "\nBalance\n0 KHT"

        addressText.text =
            "\nWallet Address\n\n$walletAddress"
    }

    private fun refreshBalance() {

        if (walletAddress == null) {

            statusText.text =
                "Create a wallet first."

            return
        }

        balanceText.text =
            "\nBalance\n0 KHT"

        statusText.text =
            "Balance refreshed.\nKhotla Testnet"
    }

    private fun showReceiveScreen() {

        if (walletAddress == null) {

            Toast.makeText(
                this,
                "Create a wallet first.",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        val layout = createLayout()

        val title = createText(
            "RECEIVE KHT",
            28f,
            Color.BLACK
        )

        val information = createText(
            "Give this address to someone\nwho wants to send you KHT.",
            17f,
            Color.DKGRAY
        )

        val address = createText(
            walletAddress!!,
            15f,
            Color.BLACK
        )

        val copyButton = Button(this)
        copyButton.text = "COPY ADDRESS"

        copyButton.setOnClickListener {

            val clipboard =
                getSystemService(
                    Context.CLIPBOARD_SERVICE
                ) as ClipboardManager

            val clip = ClipData.newPlainText(
                "KHT Wallet Address",
                walletAddress!!
            )

            clipboard.setPrimaryClip(clip)

            Toast.makeText(
                this,
                "Address copied!",
                Toast.LENGTH_SHORT
            ).show()
        }

        val backButton = Button(this)
        backButton.text = "BACK"

        backButton.setOnClickListener {
            showMainScreen()
        }

        layout.addView(title)
        layout.addView(information)
        layout.addView(address)
        layout.addView(copyButton)
        layout.addView(backButton)

        setContentView(layout)
    }

    private fun showSendScreen() {

        if (walletAddress == null) {

            Toast.makeText(
                this,
                "Create a wallet first.",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        val layout = createLayout()

        val title = createText(
            "SEND KHT",
            28f,
            Color.BLACK
        )

        val warning = createText(
            "Khotla Testnet\n\nThis is a prototype transaction screen.",
            16f,
            Color.DKGRAY
        )

        val receiverInput = EditText(this)
        receiverInput.hint = "Receiver KHT address"
        receiverInput.setSingleLine(true)

        val amountInput = EditText(this)
        amountInput.hint = "Amount in KHT"
        amountInput.inputType = 2
        amountInput.setSingleLine(true)

        val sendButton = Button(this)
        sendButton.text = "SEND KHT"

        val result = createText(
            "",
            15f,
            Color.DKGRAY
        )

        sendButton.setOnClickListener {

            val receiver =
                receiverInput.text.toString().trim()

            val amountText =
                amountInput.text.toString().trim()

            if (!receiver.startsWith("KHT")) {

                result.text =
                    "Enter a valid KHT address."

                return@setOnClickListener
            }

            val amount =
                amountText.toDoubleOrNull()

            if (amount == null || amount <= 0) {

                result.text =
                    "Enter a valid amount."

                return@setOnClickListener
            }

            /*
             * Testnet prototype:
             * No real blockchain transfer happens here yet.
             */

            saveTransaction(
                receiver,
                amount
            )

            result.text =
                "Transaction created for testnet.\n\n" +
                "To: $receiver\n" +
                "Amount: $amount KHT\n\n" +
                "Blockchain transfer will be connected in the next stage."
        }

        val backButton = Button(this)
        backButton.text = "BACK"

        backButton.setOnClickListener {
            showMainScreen()
        }

        layout.addView(title)
        layout.addView(warning)
        layout.addView(receiverInput)
        layout.addView(amountInput)
        layout.addView(sendButton)
        layout.addView(result)
        layout.addView(backButton)

        setContentView(layout)
    }

    private fun saveTransaction(
        receiver: String,
        amount: Double
    ) {

        val preferences =
            getSharedPreferences(
                preferencesName,
                Context.MODE_PRIVATE
            )

        val oldHistory =
            preferences.getString(
                historyKey,
                ""
            ) ?: ""

        val transaction =
            "SEND | $amount KHT | $receiver"

        val newHistory =
            if (oldHistory.isEmpty()) {
                transaction
            } else {
                "$oldHistory\n$transaction"
            }

        preferences
            .edit()
            .putString(
                historyKey,
                newHistory
            )
            .apply()
    }

    private fun showHistoryScreen() {

        val layout = createLayout()

        val title = createText(
            "TRANSACTION HISTORY",
            25f,
            Color.BLACK
        )

        val preferences =
            getSharedPreferences(
                preferencesName,
                Context.MODE_PRIVATE
            )

        val history =
            preferences.getString(
                historyKey,
                ""
            )

        historyText = createText(
            if (history.isNullOrEmpty()) {
                "No transactions yet."
            } else {
                history
            },
            15f,
            Color.DKGRAY
        )

        val backButton = Button(this)
        backButton.text = "BACK"

        backButton.setOnClickListener {
            showMainScreen()
        }

        layout.addView(title)
        layout.addView(historyText)
        layout.addView(backButton)

        setContentView(layout)
    }

    private fun createLayout(): LinearLayout {

        val layout = LinearLayout(this)

        layout.orientation =
            LinearLayout.VERTICAL

        layout.gravity =
            Gravity.CENTER

        layout.setPadding(
            40,
            40,
            40,
            40
        )

        return layout
    }

    private fun createText(
        text: String,
        size: Float,
        color: Int
    ): TextView {

        val view = TextView(this)

        view.text = text
        view.textSize = size
        view.setTextColor(color)
        view.gravity = Gravity.CENTER

        view.setPadding(
            10,
            10,
            10,
            10
        )

        return view
    }
}
