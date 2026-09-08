package com.khotla.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.Color
import android.os.Bundle
import android.text.InputType
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.security.MessageDigest
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

class MainActivity : AppCompatActivity() {

    private lateinit var balanceText: TextView
    private lateinit var addressText: TextView
    private lateinit var statusText: TextView
    private lateinit var walletNumberText: TextView

    private var wallet1Address: String? = null
    private var wallet2Address: String? = null

    private var wallet1Balance = 0.0
    private var wallet2Balance = 0.0

    private var selectedWallet = 1

    private val preferencesName = "khotla_wallet"

    private val wallet1AddressKey = "wallet1_address"
    private val wallet2AddressKey = "wallet2_address"

    private val wallet1BalanceKey = "wallet1_balance"
    private val wallet2BalanceKey = "wallet2_balance"

    private val historyKey = "transaction_history"

    private val apiBaseUrl =
        "https://khotla-coin-v2-1.onrender.com"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        loadWallets()
        showMainScreen()
    }

    private fun loadWallets() {

        val preferences = getSharedPreferences(
            preferencesName,
            Context.MODE_PRIVATE
        )

        wallet1Address =
            preferences.getString(
                wallet1AddressKey,
                null
            )

        wallet2Address =
            preferences.getString(
                wallet2AddressKey,
                null
            )

        wallet1Balance =
            preferences.getFloat(
                wallet1BalanceKey,
                0f
            ).toDouble()

        wallet2Balance =
            preferences.getFloat(
                wallet2BalanceKey,
                0f
            ).toDouble()
    }

    private fun createNewAddress(): String {

        val randomId =
            UUID.randomUUID().toString()

        val hash =
            MessageDigest
                .getInstance("SHA-256")
                .digest(
                    randomId.toByteArray()
                )
                .joinToString("") {
                    "%02x".format(it)
                }

        return "KHT" + hash.take(40)
    }

    private fun saveWallet1(address: String) {

        getSharedPreferences(
            preferencesName,
            Context.MODE_PRIVATE
        )
            .edit()
            .putString(
                wallet1AddressKey,
                address
            )
            .putFloat(
                wallet1BalanceKey,
                0f
            )
            .apply()
    }

    private fun saveWallet2(address: String) {

        getSharedPreferences(
            preferencesName,
            Context.MODE_PRIVATE
        )
            .edit()
            .putString(
                wallet2AddressKey,
                address
            )
            .putFloat(
                wallet2BalanceKey,
                0f
            )
            .apply()
    }

    private fun saveSelectedBalance(
        balance: Double
    ) {

        if (selectedWallet == 1) {

            wallet1Balance = balance

            getSharedPreferences(
                preferencesName,
                Context.MODE_PRIVATE
            )
                .edit()
                .putFloat(
                    wallet1BalanceKey,
                    balance.toFloat()
                )
                .apply()

        } else {

            wallet2Balance = balance

            getSharedPreferences(
                preferencesName,
                Context.MODE_PRIVATE
            )
                .edit()
                .putFloat(
                    wallet2BalanceKey,
                    balance.toFloat()
                )
                .apply()
        }
    }

    private fun getSelectedAddress(): String? {

        return if (selectedWallet == 1) {
            wallet1Address
        } else {
            wallet2Address
        }
    }

    private fun getSelectedBalance(): Double {

        return if (selectedWallet == 1) {
            wallet1Balance
        } else {
            wallet2Balance
        }
    }

    private fun showMainScreen() {

        val scrollView = ScrollView(this)

        val layout = LinearLayout(this)

        layout.orientation =
            LinearLayout.VERTICAL

        layout.gravity =
            Gravity.CENTER_HORIZONTAL

        layout.setPadding(
            28,
            35,
            28,
            35
        )

        scrollView.addView(layout)

        val title = createText(
            "KHOTLA",
            34f,
            Color.BLACK
        )

        title.setTypeface(
            null,
            android.graphics.Typeface.BOLD
        )

        val subtitle = createText(
            "WALLET",
            18f,
            Color.DKGRAY
        )

        val network = createText(
            "● KHOTLA TESTNET",
            15f,
            Color.rgb(0, 130, 70)
        )

        network.setTypeface(
            null,
            android.graphics.Typeface.BOLD
        )

        walletNumberText = createText(
            "",
            19f,
            Color.BLACK
        )

        walletNumberText.setTypeface(
            null,
            android.graphics.Typeface.BOLD
        )

        val balanceLabel = createText(
            "TOTAL BALANCE",
            14f,
            Color.DKGRAY
        )

        balanceText = createText(
            "",
            34f,
            Color.BLACK
        )

        balanceText.setTypeface(
            null,
            android.graphics.Typeface.BOLD
        )

        addressText = createText(
            "",
            13f,
            Color.DKGRAY
        )

        updateWalletDisplay()

        val copyAddressButton =
            Button(this)

        copyAddressButton.text =
            "COPY WALLET ADDRESS"

        copyAddressButton.setOnClickListener {

            copyAddress()
        }

        val sendButton =
            Button(this)

        sendButton.text =
            "SEND KHT"

        sendButton.setOnClickListener {

            showSendScreen()
        }

        val receiveButton =
            Button(this)

        receiveButton.text =
            "RECEIVE KHT"

        receiveButton.setOnClickListener {

            showReceiveScreen()
        }

        val historyButton =
            Button(this)

        historyButton.text =
            "TRANSACTION HISTORY"

        historyButton.setOnClickListener {

            showHistoryScreen()
        }

        val faucetButton =
            Button(this)

        faucetButton.text =
            "GET 100 TESTNET KHT"

        faucetButton.setOnClickListener {

            requestFaucet()
        }

        val refreshButton =
            Button(this)

        refreshButton.text =
            "REFRESH BALANCE"

        refreshButton.setOnClickListener {

            refreshBalance()
        }

        val createWalletButton =
            Button(this)

        createWalletButton.text =
            "CREATE WALLET 1"

        createWalletButton.setOnClickListener {

            createWallet1()
        }

        val secondWalletButton =
            Button(this)

        secondWalletButton.text =
            "CREATE WALLET 2"

        secondWalletButton.setOnClickListener {

            createWallet2()
        }

        val switchButton =
            Button(this)

        switchButton.text =
            "SWITCH WALLET"

        switchButton.setOnClickListener {

            switchWallet()
        }

        statusText = createText(
            "",
            14f,
            Color.DKGRAY
        )

        layout.addView(
            title,
            marginParams()
        )

        layout.addView(
            subtitle,
            marginParams()
        )

        layout.addView(
            network,
            marginParams()
        )

        layout.addView(
            walletNumberText,
            marginParams()
        )

        layout.addView(
            balanceLabel,
            marginParams()
        )

        layout.addView(
            balanceText,
            marginParams()
        )

        layout.addView(
            addressText,
            marginParams()
        )

        layout.addView(
            copyAddressButton,
            buttonParams()
        )

        layout.addView(
            sendButton,
            buttonParams()
        )

        layout.addView(
            receiveButton,
            buttonParams()
        )

        layout.addView(
            historyButton,
            buttonParams()
        )

        layout.addView(
            faucetButton,
            buttonParams()
        )

        layout.addView(
            refreshButton,
            buttonParams()
        )

        layout.addView(
            createWalletButton,
            buttonParams()
        )

        layout.addView(
            secondWalletButton,
            buttonParams()
        )

        layout.addView(
            switchButton,
            buttonParams()
        )

        layout.addView(
            statusText,
            marginParams()
        )

        setContentView(scrollView)
    }

    private fun updateWalletDisplay() {

        val address =
            getSelectedAddress()

        val balance =
            getSelectedBalance()

        walletNumberText.text =
            "WALLET $selectedWallet"

        if (address == null) {

            balanceText.text =
                "0 KHT"

            addressText.text =
                "Wallet not created yet"

            return
        }

        balanceText.text =
            "$balance KHT"

        addressText.text =
            "Wallet Address\n\n$address"
    }

    private fun copyAddress() {

        val address =
            getSelectedAddress()

        if (address == null) {

            Toast.makeText(
                this,
                "Create a wallet first.",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        val clipboard =
            getSystemService(
                Context.CLIPBOARD_SERVICE
            ) as ClipboardManager

        val clip =
            ClipData.newPlainText(
                "KHT Wallet Address",
                address
            )

        clipboard.setPrimaryClip(
            clip
        )

        Toast.makeText(
            this,
            "KHT address copied!",
            Toast.LENGTH_SHORT
        ).show()
    }

    private fun createWallet1() {

        if (wallet1Address != null) {

            selectedWallet = 1

            updateWalletDisplay()

            statusText.text =
                "Wallet 1 already exists."

            return
        }

        wallet1Address =
            createNewAddress()

        saveWallet1(
            wallet1Address!!
        )

        selectedWallet = 1

        updateWalletDisplay()

        statusText.text =
            "Wallet 1 created successfully!"
    }

    private fun createWallet2() {

        if (wallet1Address == null) {

            statusText.text =
                "Create Wallet 1 first."

            return
        }

        if (wallet2Address != null) {

            selectedWallet = 2

            updateWalletDisplay()

            statusText.text =
                "Wallet 2 already exists."

            return
        }

        wallet2Address =
            createNewAddress()

        saveWallet2(
            wallet2Address!!
        )

        selectedWallet = 2

        updateWalletDisplay()

        statusText.text =
            "Wallet 2 created successfully!"
    }

    private fun switchWallet() {

        if (wallet1Address == null) {

            statusText.text =
                "Create Wallet 1 first."

            return
        }

        if (wallet2Address == null) {

            statusText.text =
                "Create Wallet 2 first."

            return
        }

        selectedWallet =
            if (selectedWallet == 1) {
                2
            } else {
                1
            }

        updateWalletDisplay()

        statusText.text =
            "Switched to Wallet $selectedWallet"
    }

    private fun requestFaucet() {

        val address =
            getSelectedAddress()

        if (address == null) {

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
                        "address": "$address",
                        "amount": 100
                    }
                    """.trimIndent()

                val response =
                    postRequest(
                        "$apiBaseUrl/faucet",
                        json
                    )

                runOnUiThread {

                    if (
                        response.contains(
                            "\"error\""
                        )
                    ) {

                        statusText.text =
                            "Faucet error:\n$response"

                    } else {

                        saveTransaction(
                            "KHT_FAUCET",
                            address,
                            100.0,
                            "RECEIVED",
                            "CONFIRMED",
                            extractBlockNumber(
                                response
                            )
                        )

                        statusText.text =
                            "100 KHT received!\nRefreshing..."

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

        val address =
            getSelectedAddress()

        if (address == null) {

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
                        address,
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

                        saveSelectedBalance(
                            balance
                        )

                        updateWalletDisplay()

                        statusText.text =
                            "Balance updated."
                    } else {

                        statusText.text =
                            "Could not read balance."
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

        val address =
            getSelectedAddress()

        if (address == null) {

            Toast.makeText(
                this,
                "Create a wallet first.",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        val layout =
            createScreenLayout()

        val title =
            createText(
                "RECEIVE KHT",
                28f,
                Color.BLACK
            )

        val wallet =
            createText(
                "Wallet $selectedWallet",
                18f,
                Color.DKGRAY
            )

        val info =
            createText(
                "Share this address to receive KHT.",
                17f,
                Color.DKGRAY
            )

        val addressView =
            createText(
                address,
                15f,
                Color.BLACK
            )

        val copy =
            Button(this)

        copy.text =
            "COPY ADDRESS"

        copy.setOnClickListener {

            copyAddress()
        }

        val back =
            Button(this)

        back.text =
            "BACK"

        back.setOnClickListener {

            showMainScreen()
        }

        layout.addView(title)
        layout.addView(wallet)
        layout.addView(info)
        layout.addView(addressView)
        layout.addView(copy)
        layout.addView(back)

        setContentView(layout)
    }

    private fun showSendScreen() {

        val sender =
            getSelectedAddress()

        if (sender == null) {

            Toast.makeText(
                this,
                "Create a wallet first.",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        val layout =
            createScreenLayout()

        val title =
            createText(
                "SEND KHT",
                28f,
                Color.BLACK
            )

        val wallet =
            createText(
                "Sending from Wallet $selectedWallet",
                17f,
                Color.DKGRAY
            )

        val receiverInput =
            EditText(this)

        receiverInput.hint =
            "Receiver KHT address"

        receiverInput.setSingleLine(true)

        val amountInput =
            EditText(this)

        amountInput.hint =
            "Amount in KHT"

        amountInput.inputType =
            InputType.TYPE_CLASS_NUMBER or
                    InputType.TYPE_NUMBER_FLAG_DECIMAL

        amountInput.setSingleLine(true)

        val send =
            Button(this)

        send.text =
            "SEND KHT"

        val result =
            createText(
                "",
                15f,
                Color.DKGRAY
            )

        send.setOnClickListener {

            val receiver =
                receiverInput.text
                    .toString()
                    .trim()

            val amount =
                amountInput.text
                    .toString()
                    .trim()
                    .toDoubleOrNull()

            if (!receiver.startsWith("KHT")) {

                result.text =
                    "Enter a valid KHT address."

                return@setOnClickListener
            }

            if (
                amount == null ||
                amount <= 0
            ) {

                result.text =
                    "Enter a valid amount."

                return@setOnClickListener
            }

            if (
                amount >
                getSelectedBalance()
            ) {

                result.text =
                    "Insufficient KHT balance."

                return@setOnClickListener
            }

            result.text =
                "Sending to Khotla Testnet..."

            Thread {

                try {

                    val json =
                        """
                        {
                            "sender": "$sender",
                            "receiver": "$receiver",
                            "amount": $amount
                        }
                        """.trimIndent()

                    val transactionResponse =
                        postRequest(
                            "$apiBaseUrl/transaction",
                            json
                        )

                    if (
                        transactionResponse.contains(
                            "\"error\""
                        )
                    ) {

                        runOnUiThread {

                            result.text =
                                "Transaction error:\n" +
                                transactionResponse
                        }

                        return@Thread
                    }

                    val mineResponse =
                        postRequest(
                            "$apiBaseUrl/mine",
                            "{}"
                        )

                    val block =
                        extractBlockNumber(
                            mineResponse
                        )

                    runOnUiThread {

                        saveTransaction(
                            sender,
                            receiver,
                            amount,
                            "SENT",
                            "CONFIRMED",
                            block
                        )

                        result.text =
                            "Transaction confirmed!\n\n" +
                            "Amount: $amount KHT\n" +
                            "Block: $block\n\n" +
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

        val back =
            Button(this)

        back.text =
            "BACK"

        back.setOnClickListener {

            showMainScreen()
        }

        layout.addView(title)
        layout.addView(wallet)
        layout.addView(receiverInput)
        layout.addView(amountInput)
        layout.addView(send)
        layout.addView(result)
        layout.addView(back)

        setContentView(layout)
    }

    private fun saveTransaction(
        sender: String,
        receiver: String,
        amount: Double,
        type: String,
        status: String,
        block: String
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

        val time =
            SimpleDateFormat(
                "yyyy-MM-dd HH:mm:ss",
                Locale.getDefault()
            ).format(
                Date()
            )

        val transaction =
            """
            ━━━━━━━━━━━━━━━━━━
            $type KHT

            Amount: $amount KHT

            From:
            $sender

            To:
            $receiver

            Status: $status
            Block: $block
            Time: $time
            ━━━━━━━━━━━━━━━━━━
            """.trimIndent()

        val newHistory =
            if (oldHistory.isEmpty()) {
                transaction
            } else {
                "$transaction\n\n$oldHistory"
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

        val scroll =
            ScrollView(this)

        val layout =
            createScreenLayout()

        scroll.addView(layout)

        val title =
            createText(
                "TRANSACTION HISTORY",
                27f,
                Color.BLACK
            )

        val wallet =
            createText(
                "Wallet $selectedWallet",
                18f,
                Color.DKGRAY
            )

        val history =
            getSharedPreferences(
                preferencesName,
                Context.MODE_PRIVATE
            )
                .getString(
                    historyKey,
                    ""
                )

        val historyView =
            createText(
                if (
                    history.isNullOrEmpty()
                ) {
                    "No transactions yet."
                } else {
                    history
                },
                14f,
                Color.DKGRAY
            )

        historyView.gravity =
            Gravity.START

        val clear =
            Button(this)

        clear.text =
            "CLEAR LOCAL HISTORY"

        clear.setOnClickListener {

            getSharedPreferences(
                preferencesName,
                Context.MODE_PRIVATE
            )
                .edit()
                .remove(historyKey)
                .apply()

            showHistoryScreen()
        }

        val back =
            Button(this)

        back.text =
            "BACK"

        back.setOnClickListener {

            showMainScreen()
        }

        layout.addView(title)
        layout.addView(wallet)
        layout.addView(historyView)
        layout.addView(clear)
        layout.addView(back)

        setContentView(scroll)
    }

    private fun getRequest(
        urlString: String
    ): String {

        val connection =
            URL(urlString)
                .openConnection()
                    as HttpURLConnection

        connection.requestMethod =
            "GET"

        connection.connectTimeout =
            60000

        connection.readTimeout =
            60000

        return readResponse(
            connection
        )
    }

    private fun postRequest(
        urlString: String,
        json: String
    ): String {

        val connection =
            URL(urlString)
                .openConnection()
                    as HttpURLConnection

        connection.requestMethod =
            "POST"

        connection.connectTimeout =
            60000

        connection.readTimeout =
            60000

        connection.doOutput =
            true

        connection.setRequestProperty(
            "Content-Type",
            "application/json"
        )

        connection.outputStream.use {
            it.write(
                json.toByteArray()
            )
        }

        return readResponse(
            connection
        )
    }

    private fun readResponse(
        connection: HttpURLConnection
    ): String {

        val responseCode =
            connection.responseCode

        val stream =
            if (
                responseCode in 200..299
            ) {
                connection.inputStream
            } else {
                connection.errorStream
            }

        val reader =
            BufferedReader(
                InputStreamReader(
                    stream
                )
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

        return regex
            .find(response)
            ?.groupValues
            ?.getOrNull(1)
            ?.toDoubleOrNull()
    }

    private fun extractBlockNumber(
        response: String
    ): String {

        val regex =
            Regex(
                """"index"\s*:\s*(\d+)"""
            )

        return regex
            .find(response)
            ?.groupValues
            ?.getOrNull(1)
            ?: "Testnet"
    }

    private fun createScreenLayout():
            LinearLayout {

        val layout =
            LinearLayout(this)

        layout.orientation =
            LinearLayout.VERTICAL

        layout.gravity =
            Gravity.CENTER_HORIZONTAL

        layout.setPadding(
            25,
            35,
            25,
            35
        )

        return layout
    }

    private fun createText(
        text: String,
        size: Float,
        color: Int
    ): TextView {

        val view =
            TextView(this)

        view.text =
            text

        view.textSize =
            size

        view.setTextColor(
            color
        )

        view.gravity =
            Gravity.CENTER

        view.setPadding(
            10,
            12,
            10,
            12
        )

        return view
    }

    private fun marginParams():
            LinearLayout.LayoutParams {

        return LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {
            bottomMargin = 8
        }
    }

    private fun buttonParams():
            LinearLayout.LayoutParams {

        return LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {
            bottomMargin = 6
        }
    }
}
