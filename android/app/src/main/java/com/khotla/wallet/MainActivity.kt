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
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.util.UUID
import java.security.MessageDigest
import java.io.OutputStreamWriter

class MainActivity : AppCompatActivity() {

    private lateinit var balanceText: TextView
    private lateinit var addressText: TextView
    private lateinit var statusText: TextView

    private var walletAddress: String? = null
    private var walletBalance = 0.0

    private val preferencesName = "khotla_wallet"
    private val addressKey = "wallet_address"
    private val balanceKey = "wallet_balance"
    private val historyKey = "transaction_history"

    private val apiBaseUrl =
        "https://khotla-coin-v2-1.onrender.com"

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

        walletBalance = preferences.getFloat(
            balanceKey,
            0f
        ).toDouble()
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

    private fun saveBalance(balance: Double) {

        walletBalance = balance

        getSharedPreferences(
            preferencesName,
            Context.MODE_PRIVATE
        )
            .edit()
            .putFloat(balanceKey, balance.toFloat())
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

        val faucetButton = Button(this)
        faucetButton.text = "GET TESTNET KHT"

        faucetButton.setOnClickListener {
            requestFaucet()
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
        layout.addView(faucetButton)
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
            "\nBalance\n${walletBalance} KHT"

        addressText.text =
            "\nWallet Address\n\n$walletAddress"
    }

    private fun requestFaucet() {

        if (walletAddress == null) {

            statusText.text =
                "Create a wallet first."

            return
        }

        statusText.text =
            "Connecting to Khotla Testnet...\nPlease wait."

        Thread {

            try {

                val json =
                    """
                    {
                        "address": "${walletAddress}",
                        "amount": 100
                    }
                    """.trimIndent()

                val response =
                    postRequest(
                        "$apiBaseUrl/faucet",
                        json
                    )

                runOnUiThread {

                    if (response.contains("\"error\"")) {

                        statusText.text =
                            "Faucet error:\n$response"

                    } else {

                        statusText.text =
                            "100 KHT received!\nRefreshing balance..."

                        refreshBalance()
                    }
                }

            } catch (e: Exception) {

                runOnUiThread {

                    statusText.text =
                        "Connection error:\n${e.message}"
                }
            }

        }.start()
    }

    private fun refreshBalance() {

        if (walletAddress == null) {

            statusText.text =
                "Create a wallet first."

            return
        }

        statusText.text =
            "Checking Khotla Testnet..."

        Thread {

            try {

                val encodedAddress =
                    URLEncoder.encode(
                        walletAddress,
                        "UTF-8"
                    )

                val response =
                    getRequest(
                        "$apiBaseUrl/balance?address=$encodedAddress"
                    )

                val balance =
                    extractBalance(response)

                runOnUiThread {

                    if (balance != null) {

                        saveBalance(balance)
                        updateWalletDisplay()

                        statusText.text =
                            "Balance updated.\nKhotla Testnet"

                    } else {

                        statusText.text =
                            "Could not read balance.\n$response"
                    }
                }

            } catch (e: Exception) {

                runOnUiThread {

                    statusText.text =
                        "Connection error:\n${e.message}"
                }
            }

        }.start()
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
            "Khotla Testnet\n\nPrototype testnet transfer.",
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

            if (amount > walletBalance) {

                result.text =
                    "Insufficient KHT balance.\n\n" +
                    "Available: $walletBalance KHT"

                return@setOnClickListener
            }

            result.text =
                "Sending to Khotla Testnet..."

            Thread {

                try {

                    val json =
                        """
                        {
                            "sender": "$walletAddress",
                            "receiver": "$receiver",
                            "amount": $amount
                        }
                        """.trimIndent()

                    val transactionResponse =
                        postRequest(
                            "$apiBaseUrl/transaction",
                            json
                        )

                    if (transactionResponse.contains("\"error\"")) {

                        runOnUiThread {

                            result.text =
                                "Transaction error:\n$transactionResponse"
                        }

                        return@Thread
                    }

                    val mineResponse =
                        postRequest(
                            "$apiBaseUrl/mine",
                            "{}"
                        )

                    runOnUiThread {

                        saveTransaction(
                            receiver,
                            amount
                        )

                        result.text =
                            "KHT transaction submitted!\n\n" +
                            "To: $receiver\n" +
                            "Amount: $amount KHT\n\n" +
                            "Testnet block mined.\n\n" +
                            "Refreshing balance..."

                        refreshBalance()
                    }

                } catch (e: Exception) {

                    runOnUiThread {

                        result.text =
                            "Connection error:\n${e.message}"
                    }
                }

            }.start()
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

        val historyText = createText(
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

    private fun getRequest(
        urlString: String
    ): String {

        val connection =
            URL(urlString)
                .openConnection() as HttpURLConnection

        connection.requestMethod = "GET"
        connection.connectTimeout = 60000
        connection.readTimeout = 60000

        return readResponse(connection)
    }

    private fun postRequest(
        urlString: String,
        json: String
    ): String {

        val connection =
            URL(urlString)
                .openConnection() as HttpURLConnection

        connection.requestMethod = "POST"
        connection.connectTimeout = 60000
        connection.readTimeout = 60000
        connection.doOutput = true

        connection.setRequestProperty(
            "Content-Type",
            "application/json"
        )

        OutputStreamWriter(
            connection.outputStream
        ).use { writer ->

            writer.write(json)
            writer.flush()
        }

        return readResponse(connection)
    }

    private fun readResponse(
        connection: HttpURLConnection
    ): String {

        val responseCode =
            connection.responseCode

        val stream =
            if (responseCode in 200..299) {
                connection.inputStream
            } else {
                connection.errorStream
            }

        val reader =
            BufferedReader(
                InputStreamReader(stream)
            )

        return reader.use {
            it.readText()
        }
    }

    private fun extractBalance(
        response: String
    ): Double? {

        val regex =
            Regex(
                """"balance"\s*:\s*([-+]?[0-9]*\.?[0-9]+)"""
            )

        val match =
            regex.find(response)

        return match
            ?.groupValues
            ?.getOrNull(1)
            ?.toDoubleOrNull()
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
