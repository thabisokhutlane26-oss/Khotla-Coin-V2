package com.khotla.wallet

import android.os.Bundle
import android.graphics.Color
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this)
        layout.orientation = LinearLayout.VERTICAL
        layout.gravity = Gravity.CENTER
        layout.setPadding(32, 32, 32, 32)

        val title = TextView(this)
        title.text = "KHOTLA WALLET"
        title.textSize = 30f
        title.setTextColor(Color.BLACK)
        title.gravity = Gravity.CENTER

        val subtitle = TextView(this)
        subtitle.text = "Khotla Coin (KHT)"
        subtitle.textSize = 20f
        subtitle.setTextColor(Color.DKGRAY)
        subtitle.gravity = Gravity.CENTER

        val network = TextView(this)
        network.text = "\nKhotla Testnet\n\nBalance\n0 KHT\n\nWallet not created yet"
        network.textSize = 18f
        network.setTextColor(Color.DKGRAY)
        network.gravity = Gravity.CENTER

        layout.addView(title)
        layout.addView(subtitle)
        layout.addView(network)

        setContentView(layout)
    }
}
