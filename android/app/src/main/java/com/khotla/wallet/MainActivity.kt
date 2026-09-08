package com.khotla.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
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
    }

    private lateinit var root: LinearLayout
    private lateinit var statusText: TextView
    private lateinit var addressText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        buildScreen()
        checkConnection()
    }

    private fun buildScreen() {

        root = LinearLayout(this)

        root.orientation = LinearLayout.VERTICAL
        root.setPadding(40, 50, 40, 40)

        val title = TextView(this)
        title.text = "KHOTLA WALLET"
        title.textSize = 28f

        val subtitle = TextView(this)
        subtitle.text = "Khotla Coin (KHT)"
        subtitle.textSize = 18f

        val network = TextView(this)
        network.text = "\nNetwork\nKhotla Testnet"
        network.textSize = 17f

        statusText = TextView(this)
        statusText.text = "\nConnection\nChecking..."
        statusText.textSize = 17f

        val balance = TextView(this)
        balance.text = "\nBalance\n0 KHT"
        balance.textSize = 22f

        addressText = TextView(this)
        addressText.text = "\nWallet\nNo wallet created"
        addressText.textSize = 15f

        val createButton = android.widget.Button(this)
        createButton.text = "CREATE WALLET"

        createButton.setOnClickListener {
            createWallet()
        }

        val copyButton = android.widget.Button(this)
        copyButton.text = "COPY ADDRESS"

        copyButton.setOnClickListener {
            copyAddress()
        }

        val refreshButton = android.widget.Button(this)
        refreshButton.text = "REFRESH CONNECTION"

        refreshButton.setOnClickListener {
            checkConnection()
        }

        root.addView(title)
        root.addView(subtitle)
        root.addView(network)
        root.addView(statusText)
        root.addView(balance)
        root.addView(addressText)

        root.addView(createButton)
        root.addView(copyButton)
        root.addView(refreshButton)

        setContentView(root)

        loadWallet()
    }

    private fun loadWallet() {

        val prefs = getSharedPreferences(
            PREFS,
            Context.MODE_PRIVATE
        )

        val address = prefs.getString(
            KEY_ADDRESS,
            ""
        ) ?: ""

        if (address.isNotEmpty()) {
            addressText.text =
                "\nWallet\n$address"
        }
    }

    private fun createWallet() {

        val address =
            "KHT" +
                    java.util.UUID.randomUUID()
                        .toString()
                        .replace("-", "")
                        .uppercase()
                        .take(40)

        getSharedPreferences(
            PREFS,
            Context.MODE_PRIVATE
        )
            .edit()
            .putString(KEY_ADDRESS, address)
            .apply()

        addressText.text =
            "\nWallet\n$address"

        copyAddress()

        Toast.makeText(
            this,
            "Wallet created successfully 🔐",
            Toast.LENGTH_LONG
        ).show()
    }

    private fun copyAddress() {

        val prefs = getSharedPreferences(
            PREFS,
            Context.MODE_PRIVATE
        )

        val address = prefs.getString(
            KEY_ADDRESS,
            ""
        ) ?: ""

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
                "Khotla Wallet Address",
                address
            )
        )

        Toast.makeText(
            this,
            "Address copied 📋",
            Toast.LENGTH_SHORT
        ).show()
    }

    private fun checkConnection() {

        statusText.text =
            "\nConnection\nChecking..."

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
                            "\nConnection\n🟢 ONLINE"

                    } else {

                        statusText.text =
                            "\nConnection\n🔴 SERVER $code"
                    }
                }

            } catch (e: Exception) {

                runOnUiThread {

                    statusText.text =
                        "\nConnection\n🔴 OFFLINE"

                    Toast.makeText(
                        this,
                        "Connection error",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }
    }
}
