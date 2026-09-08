package com.khotla.wallet

import android.app.AlertDialog
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.text.InputType
import android.util.Base64
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import java.net.HttpURLConnection
import java.net.URL
import java.nio.charset.StandardCharsets
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    private val apiBase =
        "https://khotla-coin-v2-1.onrender.com"

    private val prefsName =
        "khotla_wallet"

    private val pinKey =
        "wallet_pin_secure"

    private val legacyPinKey =
        "wallet_pin"

    private val keystoreName =
        "AndroidKeyStore"

    private val keystoreAlias =
        "KhotlaWalletPINKey"

    private lateinit var prefs:
            android.content.SharedPreferences

    private var selectedWallet = 1

    private var wallet1Address = ""
    private var wallet2Address = ""

    private var wallet1Balance = 0.0
    private var wallet2Balance = 0.0

    private lateinit var walletNumberText: TextView
    private lateinit var balanceText: TextView
    private lateinit var addressText: TextView
    private lateinit var statusText: TextView


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        prefs = getSharedPreferences(
            prefsName,
            Context.MODE_PRIVATE
        )

        loadWalletData()

        migrateOldPinIfNeeded()

        if (getSecurePin().isNullOrEmpty()) {
            showCreatePin()
        } else {
            showEnterPin()
        }
    }


    // =========================================================
    // WALLET DATA
    // =========================================================

    private fun loadWalletData() {

        wallet1Address =
            prefs.getString(
                "wallet1_address",
                ""
            ) ?: ""

        wallet2Address =
            prefs.getString(
                "wallet2_address",
                ""
            ) ?: ""

        wallet1Balance =
            prefs.getFloat(
                "wallet1_balance",
                0f
            ).toDouble()

        wallet2Balance =
            prefs.getFloat(
                "wallet2_balance",
                0f
            ).toDouble()
    }


    // =========================================================
    // SECURE PIN
    // =========================================================

    private fun getOrCreateSecretKey(): SecretKey {

        val keyStore =
            KeyStore.getInstance(
                keystoreName
            )

        keyStore.load(null)

        if (keyStore.containsAlias(keystoreAlias)) {

            return keyStore.getKey(
                keystoreAlias,
                null
            ) as SecretKey
        }

        val keyGenerator =
            KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                keystoreName
            )

        val specification =
            KeyGenParameterSpec.Builder(
                keystoreAlias,
                KeyProperties.PURPOSE_ENCRYPT or
                        KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(
                    KeyProperties.BLOCK_MODE_GCM
                )
                .setEncryptionPaddings(
                    KeyProperties.ENCRYPTION_PADDING_NONE
                )
                .setRandomizedEncryptionRequired(true)
                .build()

        keyGenerator.init(specification)

        return keyGenerator.generateKey()
    }


    private fun saveSecurePin(pin: String) {

        try {

            val secretKey =
                getOrCreateSecretKey()

            val cipher =
                Cipher.getInstance(
                    "AES/GCM/NoPadding"
                )

            cipher.init(
                Cipher.ENCRYPT_MODE,
                secretKey
            )

            val encrypted =
                cipher.doFinal(
                    pin.toByteArray(
                        StandardCharsets.UTF_8
                    )
                )

            val iv =
                cipher.iv

            val storedValue =
                Base64.encodeToString(
                    iv,
                    Base64.NO_WRAP
                ) +
                        ":" +
                        Base64.encodeToString(
                            encrypted,
                            Base64.NO_WRAP
                        )

            prefs.edit()
                .putString(
                    pinKey,
                    storedValue
                )
                .remove(legacyPinKey)
                .apply()

        } catch (e: Exception) {

            Toast.makeText(
                this,
                "Could not secure PIN.",
                Toast.LENGTH_LONG
            ).show()
        }
    }


    private fun getSecurePin(): String? {

        try {

            val stored =
                prefs.getString(
                    pinKey,
                    null
                )

            if (stored.isNullOrEmpty()) {
                return null
            }

            val parts =
                stored.split(":")

            if (parts.size != 2) {
                return null
            }

            val iv =
                Base64.decode(
                    parts[0],
                    Base64.NO_WRAP
                )

            val encrypted =
                Base64.decode(
                    parts[1],
                    Base64.NO_WRAP
                )

            val secretKey =
                getOrCreateSecretKey()

            val cipher =
                Cipher.getInstance(
                    "AES/GCM/NoPadding"
                )

            val specification =
                javax.crypto.spec.GCMParameterSpec(
                    128,
                    iv
                )

            cipher.init(
                Cipher.DECRYPT_MODE,
                secretKey,
                specification
            )

            val decrypted =
                cipher.doFinal(
                    encrypted
                )

            return String(
                decrypted,
                StandardCharsets.UTF_8
            )

        } catch (e: Exception) {

            return null
        }
    }


    private fun migrateOldPinIfNeeded() {

        val securePin =
            prefs.getString(
                pinKey,
                null
            )

        val oldPin =
            prefs.getString(
                legacyPinKey,
                null
            )

        if (
            securePin.isNullOrEmpty() &&
            !oldPin.isNullOrEmpty()
        ) {

            saveSecurePin(oldPin)
        }
    }


    private fun isValidPin(pin: String): Boolean {

        return pin.length == 4 &&
                pin.all {
                    it.isDigit()
                }
    }


    // =========================================================
    // CREATE PIN
    // =========================================================

    private fun showCreatePin() {

        val input =
            EditText(this)

        input.inputType =
            InputType.TYPE_CLASS_NUMBER or
                    InputType.TYPE_NUMBER_VARIATION_PASSWORD

        input.hint =
            "Enter 4-digit PIN"

        input.gravity =
            Gravity.CENTER

        input.textSize =
            20f

        val layout =
            LinearLayout(this)

        layout.orientation =
            LinearLayout.VERTICAL

        layout.setPadding(
            50,
            20,
            50,
            10
        )

        layout.addView(input)

        val dialog =
            AlertDialog.Builder(this)
                .setTitle(
                    "Create Khotla PIN"
                )
                .setMessage(
                    "Create a 4-digit PIN to protect your wallet."
                )
                .setView(layout)
                .setCancelable(false)
                .setPositiveButton(
                    "SAVE PIN",
                    null
                )
                .create()

        dialog.setOnShowListener {

            dialog.getButton(
                AlertDialog.BUTTON_POSITIVE
            ).setOnClickListener {

                val pin =
                    input.text
                        .toString()

                if (!isValidPin(pin)) {

                    Toast.makeText(
                        this,
                        "PIN must be exactly 4 digits.",
                        Toast.LENGTH_SHORT
                    ).show()

                    return@setOnClickListener
                }

                saveSecurePin(pin)

                dialog.dismiss()

                initializeWallet()

                Toast.makeText(
                    this,
                    "PIN created securely!",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }

        dialog.show()
    }


    // =========================================================
    // ENTER PIN
    // =========================================================

    private fun showEnterPin() {

        val input =
            EditText(this)

        input.inputType =
            InputType.TYPE_CLASS_NUMBER or
                    InputType.TYPE_NUMBER_VARIATION_PASSWORD

        input.hint =
            "Enter PIN"

        input.gravity =
            Gravity.CENTER

        input.textSize =
            20f

        val layout =
            LinearLayout(this)

        layout.orientation =
            LinearLayout.VERTICAL

        layout.setPadding(
            50,
            20,
            50,
            10
        )

        layout.addView(input)

        val dialog =
            AlertDialog.Builder(this)
                .setTitle(
                    "Khotla Wallet"
                )
                .setMessage(
                    "Enter your 4-digit PIN to unlock your wallet."
                )
                .setView(layout)
                .setCancelable(false)
                .setPositiveButton(
                    "UNLOCK",
                    null
                )
                .create()

        dialog.setOnShowListener {

            dialog.getButton(
                AlertDialog.BUTTON_POSITIVE
            ).setOnClickListener {

                val enteredPin =
                    input.text
                        .toString()

                val savedPin =
                    getSecurePin()

                if (
                    savedPin != null &&
                    enteredPin == savedPin
                ) {

                    dialog.dismiss()

                    initializeWallet()

                    Toast.makeText(
                        this,
                        "Wallet unlocked!",
                        Toast.LENGTH_SHORT
                    ).show()

                } else {

                    Toast.makeText(
                        this,
                        "Incorrect PIN.",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }

        dialog.show()
    }


    // =========================================================
    // CHANGE PIN
    // =========================================================

    private fun showChangePin() {

        val layout =
            LinearLayout(this)

        layout.orientation =
            LinearLayout.VERTICAL

        layout.setPadding(
            40,
            10,
            40,
            10
        )

        val oldPin =
            EditText(this)

        oldPin.hint =
            "Current PIN"

        oldPin.inputType =
            InputType.TYPE_CLASS_NUMBER or
                    InputType.TYPE_NUMBER_VARIATION_PASSWORD

        layout.addView(oldPin)

        val newPin =
            EditText(this)

        newPin.hint =
            "New 4-digit PIN"

        newPin.inputType =
            InputType.TYPE_CLASS_NUMBER or
                    InputType.TYPE_NUMBER_VARIATION_PASSWORD

        layout.addView(newPin)

        val confirmPin =
            EditText(this)

        confirmPin.hint =
            "Confirm new PIN"

        confirmPin.inputType =
            InputType.TYPE_CLASS_NUMBER or
                    InputType.TYPE_NUMBER_VARIATION_PASSWORD

        layout.addView(confirmPin)

        val dialog =
            AlertDialog.Builder(this)
                .setTitle(
                    "Change PIN"
                )
                .setView(layout)
                .setNegativeButton(
                    "CANCEL",
                    null
                )
                .setPositiveButton(
                    "CHANGE PIN",
                    null
                )
                .create()

        dialog.setOnShowListener {

            dialog.getButton(
                AlertDialog.BUTTON_POSITIVE
            ).setOnClickListener {

                val current =
                    oldPin.text
                        .toString()

                val newValue =
                    newPin.text
                        .toString()

                val confirmation =
                    confirmPin.text
                        .toString()

                val saved =
                    getSecurePin()

                if (
                    saved == null ||
                    current != saved
                ) {

                    Toast.makeText(
                        this,
                        "Current PIN is incorrect.",
                        Toast.LENGTH_SHORT
                    ).show()

                    return@setOnClickListener
                }

                if (!isValidPin(newValue)) {

                    Toast.makeText(
                        this,
                        "New PIN must be exactly 4 digits.",
                        Toast.LENGTH_SHORT
                    ).show()

                    return@setOnClickListener
                }

                if (
                    newValue != confirmation
                ) {

                    Toast.makeText(
                        this,
                        "New PINs do not match.",
                        Toast.LENGTH_SHORT
                    ).show()

                    return@setOnClickListener
                }

                saveSecurePin(newValue)

                dialog.dismiss()

                Toast.makeText(
                    this,
                    "PIN changed successfully!",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }

        dialog.show()
    }


    // =========================================================
    // INITIALIZE
    // =========================================================

    private fun initializeWallet() {

        if (wallet1Address.isEmpty()) {

            wallet1Address =
                createNewAddress()

            prefs.edit()
                .putString(
                    "wallet1_address",
                    wallet1Address
                )
                .apply()
        }

        selectedWallet = 1

        createScreenLayout()

        refreshBalance()
    }


    // =========================================================
    // DASHBOARD
    // =========================================================

    private fun createScreenLayout() {

        val scrollView =
            ScrollView(this)

        val mainLayout =
            LinearLayout(this)

        mainLayout.orientation =
            LinearLayout.VERTICAL

        mainLayout.setPadding(
            30,
            30,
            30,
            40
        )

        val title =
            TextView(this)

        title.text =
            "KHOTLA"

        title.textSize =
            32f

        title.gravity =
            Gravity.CENTER

        title.setTypeface(
            null,
            android.graphics.Typeface.BOLD
        )

        mainLayout.addView(
            title,
            marginParams(
                0,
                0,
                0,
                0
            )
        )

        val subtitle =
            TextView(this)

        subtitle.text =
            "WALLET"

        subtitle.textSize =
            18f

        subtitle.gravity =
            Gravity.CENTER

        mainLayout.addView(
            subtitle,
            marginParams(
                0,
                0,
                0,
                15
            )
        )

        val network =
            TextView(this)

        network.text =
            "● KHOTLA TESTNET"

        network.textSize =
            14f

        network.gravity =
            Gravity.CENTER

        mainLayout.addView(
            network,
            marginParams(
                0,
                0,
                0,
                25
            )
        )

        walletNumberText =
            TextView(this)

        walletNumberText.textSize =
            18f

        walletNumberText.gravity =
            Gravity.CENTER

        walletNumberText.setTypeface(
            null,
            android.graphics.Typeface.BOLD
        )

        mainLayout.addView(
            walletNumberText,
            marginParams(
                0,
                0,
                0,
                10
            )
        )

        balanceText =
            TextView(this)

        balanceText.textSize =
            36f

        balanceText.gravity =
            Gravity.CENTER

        balanceText.setTypeface(
            null,
            android.graphics.Typeface.BOLD
        )

        mainLayout.addView(
            balanceText,
            marginParams(
                0,
                0,
                0,
                20
            )
        )

        addressText =
            TextView(this)

        addressText.textSize =
            12f

        addressText.gravity =
            Gravity.CENTER

        addressText.setPadding(
            15,
            15,
            15,
            15
        )

        mainLayout.addView(
            addressText,
            marginParams(
                0,
                0,
                0,
                10
            )
        )


        addButton(
            mainLayout,
            "COPY WALLET ADDRESS"
        ) {
            copyAddress()
        }


        addButton(
            mainLayout,
            "SEND KHT"
        ) {
            showSendDialog()
        }


        addButton(
            mainLayout,
            "RECEIVE KHT"
        ) {
            showReceiveDialog()
        }


        addButton(
            mainLayout,
            "TRANSACTION HISTORY"
        ) {
            showTransactionHistory()
        }


        addButton(
            mainLayout,
            "GET 100 TESTNET KHT"
        ) {
            requestFaucet()
        }


        addButton(
            mainLayout,
            "REFRESH BALANCE"
        ) {
            refreshBalance()
        }


        addButton(
            mainLayout,
            "CREATE WALLET 1"
        ) {
            createWallet1()
        }


        addButton(
            mainLayout,
            "CREATE WALLET 2"
        ) {
            createWallet2()
        }


        addButton(
            mainLayout,
            "SWITCH WALLET"
        ) {
            switchWallet()
        }


        addButton(
            mainLayout,
            "CHANGE PIN"
        ) {
            showChangePin()
        }


        addButton(
            mainLayout,
            "LOCK WALLET"
        ) {
            lockWallet()
        }


        statusText =
            TextView(this)

        statusText.text =
            "Ready"

        statusText.textSize =
            14f

        statusText.gravity =
            Gravity.CENTER

        mainLayout.addView(
            statusText,
            marginParams(
                0,
                20,
                0,
                0
            )
        )

        scrollView.addView(
            mainLayout
        )

        setContentView(
            scrollView
        )

        updateDashboard()
    }


    private fun addButton(
        layout: LinearLayout,
        text: String,
        action: () -> Unit
    ) {

        val button =
            Button(this)

        button.text =
            text

        button.setOnClickListener {
            action()
        }

        layout.addView(
            button,
            buttonParams()
        )
    }


    // =========================================================
    // WALLET
    // =========================================================

    private fun createNewAddress(): String {

        val random =
            java.util.UUID
                .randomUUID()
                .toString()
                .replace(
                    "-",
                    ""
                )

        return "KHT" +
                random +
                java.util.UUID
                    .randomUUID()
                    .toString()
                    .replace(
                        "-",
                        ""
                    )
                    .substring(
                        0,
                        7
                    )
    }


    private fun createWallet1() {

        if (
            wallet1Address.isNotEmpty()
        ) {

            Toast.makeText(
                this,
                "Wallet 1 already exists.",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        wallet1Address =
            createNewAddress()

        prefs.edit()
            .putString(
                "wallet1_address",
                wallet1Address
            )
            .apply()

        selectedWallet = 1

        updateDashboard()

        Toast.makeText(
            this,
            "Wallet 1 created!",
            Toast.LENGTH_SHORT
        ).show()
    }


    private fun createWallet2() {

        if (
            wallet2Address.isNotEmpty()
        ) {

            Toast.makeText(
                this,
                "Wallet 2 already exists.",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        wallet2Address =
            createNewAddress()

        prefs.edit()
            .putString(
                "wallet2_address",
                wallet2Address
            )
            .apply()

        selectedWallet = 2

        updateDashboard()

        Toast.makeText(
            this,
            "Wallet 2 created!",
            Toast.LENGTH_SHORT
        ).show()
    }


    private fun switchWallet() {

        if (
            wallet2Address.isEmpty()
        ) {

            Toast.makeText(
                this,
                "Create Wallet 2 first.",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        selectedWallet =
            if (
                selectedWallet == 1
            ) 2
            else 1

        updateDashboard()

        refreshBalance()
    }


    private fun currentAddress():
            String {

        return if (
            selectedWallet == 1
        ) {
            wallet1Address
        } else {
            wallet2Address
        }
    }


    private fun currentBalance():
            Double {

        return if (
            selectedWallet == 1
        ) {
            wallet1Balance
        } else {
            wallet2Balance
        }
    }


    private fun updateDashboard() {

        if (
            !::walletNumberText
                .isInitialized
        ) {
            return
        }

        walletNumberText.text =
            "WALLET $selectedWallet"

        balanceText.text =
            String.format(
                "%.2f KHT",
                currentBalance()
            )

        addressText.text =
            currentAddress()
    }


    private fun copyAddress() {

        val clipboard =
            getSystemService(
                Context.CLIPBOARD_SERVICE
            ) as ClipboardManager

        clipboard.setPrimaryClip(
            ClipData.newPlainText(
                "KHT Wallet Address",
                currentAddress()
            )
        )

        Toast.makeText(
            this,
            "KHT address copied!",
            Toast.LENGTH_SHORT
        ).show()
    }


    // =========================================================
    // BALANCE
    // =========================================================

    private fun refreshBalance() {

        val address =
            currentAddress()

        if (address.isEmpty()) {
            return
        }

        statusText.text =
            "Connecting to Khotla Testnet..."

        thread {

            try {

                val url =
                    URL(
                        "$apiBase/balance?address=$address"
                    )

                val connection =
                    url.openConnection()
                            as HttpURLConnection

                connection.requestMethod =
                    "GET"

                connection.connectTimeout =
                    15000

                connection.readTimeout =
                    15000

                val response =
                    connection.inputStream
                        .bufferedReader()
                        .readText()

                val balance =
                    Regex(
                        "\"balance\"\\s*:\\s*([0-9.]+)"
                    )
                        .find(response)
                        ?.groupValues
                        ?.get(1)
                        ?.toDoubleOrNull()
                        ?: 0.0

                connection.disconnect()

                runOnUiThread {

                    if (
                        selectedWallet == 1
                    ) {

                        wallet1Balance =
                            balance

                        prefs.edit()
                            .putFloat(
                                "wallet1_balance",
                                balance.toFloat()
                            )
                            .apply()

                    } else {

                        wallet2Balance =
                            balance

                        prefs.edit()
                            .putFloat(
                                "wallet2_balance",
                                balance.toFloat()
                            )
                            .apply()
                    }

                    updateDashboard()

                    statusText.text =
                        "Balance updated."
                }

            } catch (e: Exception) {

                runOnUiThread {

                    statusText.text =
                        "Connection error: ${e.message}"
                }
            }
        }
    }


    // =========================================================
    // FAUCET
    // =========================================================

    private fun requestFaucet() {

        val address =
            currentAddress()

        statusText.text =
            "Requesting 100 testnet KHT..."

        thread {

            try {

                val url =
                    URL(
                        "$apiBase/faucet"
                    )

                val connection =
                    url.openConnection()
                            as HttpURLConnection

                connection.requestMethod =
                    "POST"

                connection.doOutput =
                    true

                connection.setRequestProperty(
                    "Content-Type",
                    "application/json"
                )

                val body =
                    """{"address":"$address","amount":100}"""

                connection.outputStream.use {
                    it.write(
                        body.toByteArray()
                    )
                }

                if (
                    connection.responseCode !in 200..299
                ) {

                    throw Exception(
                        "Faucet request failed."
                    )
                }

                connection.disconnect()

                runOnUiThread {

                    addHistory(
                        "RECEIVED",
                        100.0,
                        "KHT_FAUCET",
                        address,
                        "SUCCESS"
                    )

                    statusText.text =
                        "100 KHT received!"

                    refreshBalance()
                }

            } catch (e: Exception) {

                runOnUiThread {

                    statusText.text =
                        "Faucet error: ${e.message}"
                }
            }
        }
    }


    // =========================================================
    // SEND
    // =========================================================

    private fun showSendDialog() {

        val layout =
            LinearLayout(this)

        layout.orientation =
            LinearLayout.VERTICAL

        layout.setPadding(
            40,
            10,
            40,
            10
        )

        val receiverInput =
            EditText(this)

        receiverInput.hint =
            "Receiver KHT address"

        layout.addView(
            receiverInput
        )

        val amountInput =
            EditText(this)

        amountInput.hint =
            "Amount"

        amountInput.inputType =
            InputType.TYPE_CLASS_NUMBER or
                    InputType.TYPE_NUMBER_FLAG_DECIMAL

        layout.addView(
            amountInput
        )

        val dialog =
            AlertDialog.Builder(this)
                .setTitle(
                    "Send KHT"
                )
                .setView(layout)
                .setNegativeButton(
                    "CANCEL",
                    null
                )
                .setPositiveButton(
                    "SEND",
                    null
                )
                .create()

        dialog.setOnShowListener {

            dialog.getButton(
                AlertDialog.BUTTON_POSITIVE
            ).setOnClickListener {

                val receiver =
                    receiverInput.text
                        .toString()
                        .trim()

                val amount =
                    amountInput.text
                        .toString()
                        .toDoubleOrNull()

                if (
                    !receiver.startsWith("KHT")
                ) {

                    Toast.makeText(
                        this,
                        "Invalid KHT receiver address.",
                        Toast.LENGTH_SHORT
                    ).show()

                    return@setOnClickListener
                }

                if (
                    amount == null ||
                    amount <= 0
                ) {

                    Toast.makeText(
                        this,
                        "Enter a valid amount.",
                        Toast.LENGTH_SHORT
                    ).show()

                    return@setOnClickListener
                }

                if (
                    amount > currentBalance()
                ) {

                    Toast.makeText(
                        this,
                        "Insufficient KHT balance.",
                        Toast.LENGTH_SHORT
                    ).show()

                    return@setOnClickListener
                }

                dialog.dismiss()

                sendKht(
                    receiver,
                    amount
                )
            }
        }

        dialog.show()
    }


    private fun sendKht(
        receiver: String,
        amount: Double
    ) {

        val sender =
            currentAddress()

        statusText.text =
            "Sending KHT..."

        thread {

            try {

                val transactionUrl =
                    URL(
                        "$apiBase/transaction"
                    )

                val connection =
                    transactionUrl.openConnection()
                            as HttpURLConnection

                connection.requestMethod =
                    "POST"

                connection.doOutput =
                    true

                connection.setRequestProperty(
                    "Content-Type",
                    "application/json"
                )

                val body =
                    """{"sender":"$sender","receiver":"$receiver","amount":$amount}"""

                connection.outputStream.use {
                    it.write(
                        body.toByteArray()
                    )
                }

                if (
                    connection.responseCode !in 200..299
                ) {

                    throw Exception(
                        "Transaction rejected."
                    )
                }

                connection.disconnect()


                val mineUrl =
                    URL(
                        "$apiBase/mine"
                    )

                val mineConnection =
                    mineUrl.openConnection()
                            as HttpURLConnection

                mineConnection.requestMethod =
                    "POST"

                mineConnection.doOutput =
                    true

                mineConnection.setRequestProperty(
                    "Content-Type",
                    "application/json"
                )

                mineConnection.outputStream.use {
                    it.write(
                        "{}".toByteArray()
                    )
                }

                val mineResponse =
                    mineConnection.inputStream
                        .bufferedReader()
                        .readText()

                val block =
                    Regex(
                        "\"index\"\\s*:\\s*(\\d+)"
                    )
                        .find(
                            mineResponse
                        )
                        ?.groupValues
                        ?.get(1)
                        ?: "N/A"

                mineConnection.disconnect()

                runOnUiThread {

                    addHistory(
                        "SENT",
                        amount,
                        sender,
                        receiver,
                        "SUCCESS",
                        block
                    )

                    statusText.text =
                        "$amount KHT sent successfully."

                    refreshBalance()
                }

            } catch (e: Exception) {

                runOnUiThread {

                    statusText.text =
                        "Send error: ${e.message}"
                }
            }
        }
    }


    // =========================================================
    // RECEIVE
    // =========================================================

    private fun showReceiveDialog() {

        AlertDialog.Builder(this)
            .setTitle(
                "Receive KHT"
            )
            .setMessage(
                "Give this address to the person sending you KHT:\n\n" +
                        currentAddress()
            )
            .setPositiveButton(
                "COPY ADDRESS"
            ) { _, _ ->

                copyAddress()
            }
            .setNegativeButton(
                "CLOSE",
                null
            )
            .show()
    }


    // =========================================================
    // TRANSACTION HISTORY
    // =========================================================

    private fun addHistory(
        type: String,
        amount: Double,
        from: String,
        to: String,
        status: String,
        block: String = "N/A"
    ) {

        val oldHistory =
            prefs.getString(
                "transaction_history",
                ""
            ) ?: ""

        val time =
            java.text.SimpleDateFormat(
                "yyyy-MM-dd HH:mm:ss",
                java.util.Locale.getDefault()
            ).format(
                java.util.Date()
            )

        val entry =
            "$type|$amount|$from|$to|$status|$block|$time"

        val newHistory =
            if (
                oldHistory.isEmpty()
            ) {
                entry
            } else {
                "$entry\n$oldHistory"
            }

        prefs.edit()
            .putString(
                "transaction_history",
                newHistory
            )
            .apply()
    }


    private fun showTransactionHistory() {

        val history =
            prefs.getString(
                "transaction_history",
                ""
            ) ?: ""

        val layout =
            LinearLayout(this)

        layout.orientation =
            LinearLayout.VERTICAL

        layout.setPadding(
            30,
            20,
            30,
            20
        )

        val text =
            TextView(this)

        text.textSize =
            13f

        if (
            history.isEmpty()
        ) {

            text.text =
                "No transactions yet."

        } else {

            val builder =
                StringBuilder()

            history
                .split("\n")
                .forEach { entry ->

                    val parts =
                        entry.split("|")

                    if (
                        parts.size >= 7
                    ) {

                        builder.append(
                            "━━━━━━━━━━━━━━━━━━\n"
                        )

                        builder.append(
                            "${parts[0]}  ${parts[1]} KHT\n"
                        )

                        builder.append(
                            "From: ${parts[2]}\n"
                        )

                        builder.append(
                            "To: ${parts[3]}\n"
                        )

                        builder.append(
                            "Status: ${parts[4]}\n"
                        )

                        builder.append(
                            "Block: ${parts[5]}\n"
                        )

                        builder.append(
                            "Time: ${parts[6]}\n"
                        )
                    }
                }

            builder.append(
                "━━━━━━━━━━━━━━━━━━"
            )

            text.text =
                builder.toString()
        }

        layout.addView(
            text
        )

        AlertDialog.Builder(this)
            .setTitle(
                "Transaction History"
            )
            .setView(layout)
            .setPositiveButton(
                "CLOSE",
                null
            )
            .setNeutralButton(
                "CLEAR LOCAL HISTORY"
            ) { _, _ ->

                prefs.edit()
                    .remove(
                        "transaction_history"
                    )
                    .apply()

                Toast.makeText(
                    this,
                    "Local history cleared.",
                    Toast.LENGTH_SHORT
                ).show()
            }
            .show()
    }


    // =========================================================
    // LOCK
    // =========================================================

    private fun lockWallet() {

        Toast.makeText(
            this,
            "Wallet locked.",
            Toast.LENGTH_SHORT
        ).show()

        showEnterPin()
    }


    // =========================================================
    // UI HELPERS
    // =========================================================

    private fun buttonParams():
            LinearLayout.LayoutParams {

        return LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {

            setMargins(
                0,
                6,
                0,
                6
            )
        }
    }


    private fun marginParams(
        left: Int,
        top: Int,
        right: Int,
        bottom: Int
    ):
            LinearLayout.LayoutParams {

        return LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {

            setMargins(
                left,
                top,
                right,
                bottom
            )
        }
    }
}
