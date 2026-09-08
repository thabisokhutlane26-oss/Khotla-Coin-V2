package com.khotla.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    companion object {
        private const val API_URL =
            "https://khotla-coin-v2-1.onrender.com"

        private const val PREFS =
            "khotla_wallet"

        private const val KEY_ADDRESS =
            "wallet_address"

        private const val KEY_BALANCE =
            "wallet_balance"

        private const val KEY_HISTORY =
            "wallet_history"
    }

    private lateinit var balanceText: TextView
    private lateinit var addressText: TextView
    private lateinit var statusText: TextView
    private lateinit var historyText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        buildDashboard()
        loadWallet()
        checkConnection()
    }

    private fun buildDashboard() {

        val scroll = ScrollView(this)

        val root = LinearLayout(this)
        root.orientation = LinearLayout.VERTICAL
        root.setPadding(35, 40, 35, 40)

        val title = TextView(this)
        title.text = "KHOTLA WALLET"
        title.textSize = 30f

        val subtitle = TextView(this)
        subtitle.text = "Khotla Coin • KHT"
        subtitle.textSize = 18f

        val network = TextView(this)
        network.text = "\n🌐 Network\nKhotla Testnet"
        network.textSize = 17f

        statusText = TextView(this)
        statusText.text = "\n🔄 Connection\nChecking..."
        statusText.textSize = 17f

        balanceText = TextView(this)
        balanceText.text = "\n💰 Balance\n0 KHT"
        balanceText.textSize = 25f

        addressText = TextView(this)
        addressText.text = "\n👛 Wallet\nNo wallet created"
        addressText.textSize = 14f

        val createButton = Button(this)
        createButton.text = "CREATE WALLET"

        createButton.setOnClickListener {
            createWallet()
        }

        val faucetButton = Button(this)
        faucetButton.text = "🚰 GET 100 KHT"

        faucetButton.setOnClickListener {
            faucet()
        }

        val sendButton = Button(this)
        sendButton.text = "📤 SEND KHT"

        sendButton.setOnClickListener {
            sendKht()
        }

        val receiveButton = Button(this)
        receiveButton.text = "📥 RECEIVE KHT"

        receiveButton.setOnClickListener {
            receive()
        }

        val copyButton = Button(this)
        copyButton.text = "📋 COPY ADDRESS"

        copyButton.setOnClickListener {
            copyAddress()
        }

        val refreshButton = Button(this)
        refreshButton.text = "🔄 REFRESH"

        refreshButton.setOnClickListener {
            loadWallet()
            checkConnection()
        }

        val historyTitle = TextView(this)
        historyTitle.text = "\n📜 TRANSACTION HISTORY"
        historyTitle.textSize = 20f

        historyText = TextView(this)
        historyText.text = "No transactions yet."
        historyText.textSize = 15f

        root.addView(title)
        root.addView(subtitle)
        root.addView(network)
        root.addView(statusText)
        root.addView(balanceText)
        root.addView(addressText)

        root.addView(createButton)
        root.addView(faucetButton)
        root.addView(sendButton)
        root.addView(receiveButton)
        root.addView(copyButton)
        root.addView(refreshButton)

        root.addView(historyTitle)
        root.addView(historyText)

        scroll.addView(root)

        setContentView(scroll)
    }

    private fun loadWallet() {

        val prefs =
            getSharedPreferences(PREFS, Context.MODE_PRIVATE)

        val address =
            prefs.getString(KEY_ADDRESS, "") ?: ""

        val balance =
            prefs.getFloat(KEY_BALANCE, 0f)

        addressText.text =
            if (address.isEmpty()) {
                "\n👛 Wallet\nNo wallet created"
            } else {
                "\n👛 Wallet\n$address"
            }

        balanceText.text =
            "\n💰 Balance\n$balance KHT"

        historyText.text =
            prefs.getString(
                KEY_HISTORY,
                "No transactions yet."
            )
                ?: "No transactions yet."
    }

    private fun createWallet() {

        val existing =
            getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .getString(KEY_ADDRESS, "")

        if (!existing.isNullOrEmpty()) {

            Toast.makeText(
                this,
                "Wallet already exists",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        val address =
            "KHT" +
                    java.util.UUID.randomUUID()
                        .toString()
                        .replace("-", "")
                        .uppercase()
                        .take(40)

        getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_ADDRESS, address)
            .putFloat(KEY_BALANCE, 0f)
            .apply()

        loadWallet()

        copyAddress()

        Toast.makeText(
            this,
            "Wallet created 🔐",
            Toast.LENGTH_LONG
        ).show()
    }

    private fun faucet() {

        val prefs =
            getSharedPreferences(PREFS, Context.MODE_PRIVATE)

        val address =
            prefs.getString(KEY_ADDRESS, "") ?: ""

        if (address.isEmpty()) {

            Toast.makeText(
                this,
                "Create a wallet first",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        val oldBalance =
            prefs.getFloat(KEY_BALANCE, 0f)

        val newBalance =
            oldBalance + 100f

        prefs.edit()
            .putFloat(KEY_BALANCE, newBalance)
            .apply()

        addHistory(
            "🚰 Faucet +100 KHT"
        )

        loadWallet()

        Toast.makeText(
            this,
            "100 KHT added",
            Toast.LENGTH_LONG
        ).show()
    }

    private fun sendKht() {

        val prefs =
            getSharedPreferences(PREFS, Context.MODE_PRIVATE)

        val balance =
            prefs.getFloat(KEY_BALANCE, 0f)

        if (balance <= 0f) {

            Toast.makeText(
                this,
                "Insufficient KHT",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        val input = EditText(this)

        input.hint = "Recipient address"

        AlertDialogBuilder(
            "Send KHT",
            input,
            "NEXT"
        ) {

            val recipient =
                input.text.toString().trim()

            if (recipient.isEmpty()) {

                Toast.makeText(
                    this,
                    "Enter recipient address",
                    Toast.LENGTH_SHORT
                ).show()

                return@AlertDialogBuilder
            }

            val amountInput = EditText(this)

            amountInput.hint = "Amount KHT"
            amountInput.inputType =
                android.text.InputType.TYPE_CLASS_NUMBER or
                        android.text.InputType.TYPE_NUMBER_FLAG_DECIMAL

            AlertDialogBuilder(
                "Send Amount",
                amountInput,
                "SEND"
            ) {

                val amount =
                    amountInput.text.toString()
                        .toFloatOrNull()

                if (amount == null || amount <= 0f) {

                    Toast.makeText(
                        this,
                        "Invalid amount",
                        Toast.LENGTH_SHORT
                    ).show()

                    return@AlertDialogBuilder
                }

                if (amount > balance) {

                    Toast.makeText(
                        this,
                        "Insufficient balance",
                        Toast.LENGTH_SHORT
                    ).show()

                    return@AlertDialogBuilder
                }

                prefs.edit()
                    .putFloat(
                        KEY_BALANCE,
                        balance - amount
                    )
                    .apply()

                addHistory(
                    "📤 Sent $amount KHT to $recipient"
                )

                loadWallet()

                Toast.makeText(
                    this,
                    "Transaction recorded",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }

    private fun receive() {

        val address =
            getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .getString(KEY_ADDRESS, "") ?: ""

        if (address.isEmpty()) {

            Toast.makeText(
                this,
                "Create a wallet first",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        android.app.AlertDialog.Builder(this)
            .setTitle("📥 Receive KHT")
            .setMessage(
                "Send KHT to this wallet address:\n\n$address"
            )
            .setPositiveButton("COPY") { _, _ ->
                copyAddress()
            }
            .setNegativeButton("CLOSE", null)
            .show()
    }

    private fun copyAddress() {

        val address =
            getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .getString(KEY_ADDRESS, "") ?: ""

        if (address.isEmpty()) {

            Toast.makeText(
                this,
                "Create a wallet first",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        val clipboard =
            getSystemService(
                Context.CLIPBOARD_SERVICE
            ) as ClipboardManager

        clipboard.setPrimaryClip(
            ClipData.newPlainText(
                "Khotla Address",
                address
            )
        )

        Toast.makeText(
            this,
            "Address copied 📋",
            Toast.LENGTH_SHORT
        ).show()
    }

    private fun addHistory(transaction: String) {

        val prefs =
            getSharedPreferences(PREFS, Context.MODE_PRIVATE)

        val old =
            prefs.getString(
                KEY_HISTORY,
                ""
            ) ?: ""

        val updated =
            if (old.isEmpty()) {
                transaction
            } else {
                "$transaction\n$old"
            }

        prefs.edit()
            .putString(KEY_HISTORY, updated)
            .apply()
    }

    private fun checkConnection() {

        statusText.text =
            "\n🔄 Connection\nChecking..."

        thread {

            try {

                val connection =
                    URL(API_URL)
                        .openConnection()
                            as HttpURLConnection

                connection.requestMethod = "GET"
                connection.connectTimeout = 10000
                connection.readTimeout = 10000

                val code =
                    connection.responseCode

                connection.disconnect()

                runOnUiThread {

                    if (code in 200..299) {

                        statusText.text =
                            "\n🟢 Connection\nONLINE"

                    } else {

                        statusText.text =
                            "\n🔴 Connection\nSERVER $code"
                    }
                }

            } catch (e: Exception) {

                runOnUiThread {

                    statusText.text =
                        "\n🔴 Connection\nOFFLINE"
                }
            }
        }
    }

    private fun AlertDialogBuilder(
        title: String,
        view: EditText,
        button: String,
        action: () -> Unit
    ) {

        android.app.AlertDialog.Builder(this)
            .setTitle(title)
            .setView(view)
            .setPositiveButton(button) { _, _ ->
                action()
            }
            .setNegativeButton("CANCEL", null)
            .show()
    }
}
