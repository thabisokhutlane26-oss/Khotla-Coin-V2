package com.khotla.wallet

import android.os.Bundle
import android.graphics.Color
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.security.MessageDigest
import java.util.UUID

class MainActivity : AppCompatActivity() {

    private lateinit var balanceText: TextView
    private lateinit var addressText: TextView
    private lateinit var statusText: TextView

    private var walletAddress: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        createWalletScreen()
    }

    private fun createWalletScreen() {

        val layout = LinearLayout(this)
        layout.orientation = LinearLayout.VERTICAL
        layout.gravity = Gravity.CENTER
        layout.setPadding(40, 40, 40, 40)

        val title = TextView(this)
        title.text = "KHOTLA WALLET"
        title.textSize = 30f
        title.setTextColor(Color.BLACK)
        title.gravity = Gravity.CENTER

        val coin = TextView(this)
        coin.text = "Khotla Coin (KHT)"
        coin.textSize = 20f
        coin.setTextColor(Color.DKGRAY)
        coin.gravity = Gravity.CENTER

        val network = TextView(this)
        network.text = "Khotla Testnet"
        network.textSize = 16f
        network.setTextColor(Color.DKGRAY)
        network.gravity = Gravity.CENTER

        balanceText = TextView(this)
        balanceText.text = "\nBalance\n0 KHT"
        balanceText.textSize = 24f
        balanceText.setTextColor(Color.BLACK)
        balanceText.gravity = Gravity.CENTER

        addressText = TextView(this)
        addressText.text = "\nWallet not created yet"
        addressText.textSize = 15f
        addressText.setTextColor(Color.DKGRAY)
        addressText.gravity = Gravity.CENTER

        val createButton = Button(this)
        createButton.text = "CREATE WALLET"

        val refreshButton = Button(this)
        refreshButton.text = "REFRESH BALANCE"

        statusText = TextView(this)
        statusText.text = ""
        statusText.textSize = 14f
        statusText.gravity = Gravity.CENTER

        createButton.setOnClickListener {
            createWallet()
        }

        refreshButton.setOnClickListener {
            refreshBalance()
        }

        layout.addView(title)
        layout.addView(coin)
        layout.addView(network)
        layout.addView(balanceText)
        layout.addView(addressText)
        layout.addView(createButton)
        layout.addView(refreshButton)
        layout.addView(statusText)

        setContentView(layout)
    }

    private fun createWallet() {

        val randomId = UUID.randomUUID().toString()

        val hash = MessageDigest
            .getInstance("SHA-256")
            .digest(randomId.toByteArray())
            .joinToString("") { "%02x".format(it) }

        walletAddress = "KHT" + hash.take(40)

        addressText.text =
            "\nWallet Address\n\n$walletAddress"

        balanceText.text =
            "\nBalance\n0 KHT"

        statusText.text =
            "\nWallet created successfully!\nKhotla Testnet"

    }

    private fun refreshBalance() {

        if (walletAddress == null) {

            statusText.text =
                "\nCreate a wallet first."

            return
        }

        balanceText.text =
            "\nBalance\n0 KHT"

        statusText.text =
            "\nBalance refreshed.\nKhotla Testnet"
    }
}
