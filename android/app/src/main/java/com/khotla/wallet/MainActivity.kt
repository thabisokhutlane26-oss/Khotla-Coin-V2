package com.khotla.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.edit
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
    }

    private lateinit var prefs: SharedPreferences

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        prefs = getSharedPreferences(
            PREFS,
            Context.MODE_PRIVATE
        )

        showDashboard()
        checkConnection()
    }

    private fun showDashboard() {

        val address = prefs.getString(
            KEY_ADDRESS,
            ""
        ) ?: ""

        val balance = prefs.getFloat(
            KEY_BALANCE,
            0f
        )

        val text = """
            
            KHOTLA WALLET
            
            Khotla Coin
            KHT
            
            Network:
            Khotla Testnet
            
            -------------------------
            
            Balance:
            $balance KHT
            
            Wallet:
            ${if (address.isEmpty()) "No wallet created" else address}
            
            -------------------------
            
            Connection:
            Checking...
            
        """.trimIndent()

        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Khotla Wallet")
            .setMessage(text)
            .setPositiveButton("Refresh") { _, _ ->
                checkConnection()
            }
            .setNegativeButton("Create Wallet") { _, _ ->
                createWallet()
            }
            .show()
    }

    private fun checkConnection() {

        thread {

            try {

                val url = URL(API_URL)

                val connection =
                    url.openConnection()
                            as HttpURLConnection

                connection.requestMethod = "GET"
                connection.connectTimeout = 10000
                connection.readTimeout = 10000

                val responseCode =
                    connection.responseCode

                connection.disconnect()

                runOnUiThread {

                    if (responseCode in 200..299) {

                        Toast.makeText(
                            this,
                            "Khotla Testnet: ONLINE 🟢",
                            Toast.LENGTH_LONG
                        ).show()

                    } else {

                        Toast.makeText(
                            this,
                            "Server returned: $responseCode",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }

            } catch (error: Exception) {

                runOnUiThread {

                    Toast.makeText(
                        this,
                        "Connection error: ${error.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }
    }

    private fun createWallet() {

        val address =
            "KHT" + java.util.UUID.randomUUID()
                .toString()
                .replace("-", "")
                .take(40)

        prefs.edit {

            putString(
                KEY_ADDRESS,
                address
            )

            putFloat(
                KEY_BALANCE,
                0f
            )
        }

        copyToClipboard(address)

        AlertDialog.Builder(this)
            .setTitle("Wallet Created 🔐")
            .setMessage(
                """
                
                Your Khotla wallet has been created.
                
                Address:
                
                $address
                
                The address has also been copied to your clipboard.
                
                """.trimIndent()
            )
            .setPositiveButton("OK", null)
            .show()
    }

    private fun copyToClipboard(
        text: String
    ) {

        val clipboard =
            getSystemService(
                Context.CLIPBOARD_SERVICE
            ) as ClipboardManager

        clipboard.setPrimaryClip(
            ClipData.newPlainText(
                "Khotla Address",
                text
            )
        )

        Toast.makeText(
            this,
            "Address copied",
            Toast.LENGTH_SHORT
        ).show()
    }
}
