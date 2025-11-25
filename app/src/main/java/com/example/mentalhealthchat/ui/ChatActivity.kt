package com.example.mentalhealthchat.ui

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.example.mentalhealthchat.R
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ChatActivity : AppCompatActivity() {

    private lateinit var chatContainer: LinearLayout
    private lateinit var chatScroll: ScrollView
    private lateinit var inputBox: EditText
    private lateinit var sendBtn: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        chatContainer = findViewById(R.id.chatContainer)
        chatScroll = findViewById(R.id.chatScroll)
        inputBox = findViewById(R.id.inputBox)
        sendBtn = findViewById(R.id.sendBtn)

        // Load saved email
        val email = getSharedPreferences("app", MODE_PRIVATE)
            .getString("email", "")!!

        sendBtn.setOnClickListener {
            val message = inputBox.text.toString().trim()

            if (message.isEmpty()) return@setOnClickListener

            // Show user message bubble
            addMessage(message, isUser = true)

            inputBox.setText("")  // clear box

            val req = ChatRequest(email, message)

            // API call
            RetrofitClient.instance.chat(req)
                .enqueue(object : Callback<ChatResponse> {
                    override fun onResponse(
                        call: Call<ChatResponse>,
                        response: Response<ChatResponse>
                    ) {
                        val res = response.body()

                        if (res == null) {
                            addMessage("Error: Empty response", false)
                            return
                        }

                        if (!res.allowed) {
                            addMessage("Free limit reached. Please upgrade.", false)
                            return
                        }

                        addMessage(res.reply ?: "No reply", false)
                    }

                    override fun onFailure(call: Call<ChatResponse>, t: Throwable) {
                        addMessage("Error: ${t.message}", false)
                    }
                })
        }
    }

    // Chat bubble renderer
    private fun addMessage(text: String, isUser: Boolean) {
        val tv = TextView(this)
        tv.text = text
        tv.textSize = 16f

        val params = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        )
        params.setMargins(0, 10, 0, 10)

        if (isUser) {
            params.gravity = android.view.Gravity.END
            tv.setBackgroundResource(R.drawable.chat_user)
        } else {
            params.gravity = android.view.Gravity.START
            tv.setBackgroundResource(R.drawable.chat_bot)
        }

        tv.layoutParams = params
        tv.setPadding(24, 16, 24, 16)

        chatContainer.addView(tv)

        // Auto scroll to bottom
        chatScroll.post { chatScroll.fullScroll(ScrollView.FOCUS_DOWN) }
    }
}
