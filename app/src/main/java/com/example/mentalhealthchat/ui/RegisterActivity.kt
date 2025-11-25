package com.example.mentalhealthchat.ui

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.example.mentalhealthchat.R
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class RegisterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        val emailEt = findViewById<EditText>(R.id.emailEt)
        val ageEt = findViewById<EditText>(R.id.ageEt)
        val sexEt = findViewById<EditText>(R.id.sexEt)
        val btn = findViewById<Button>(R.id.registerBtn)

        btn.setOnClickListener {
            val email = emailEt.text.toString()
            val age = ageEt.text.toString().toInt()
            val sex = sexEt.text.toString()

            val req = RegisterRequest(email, age, sex)

            RetrofitClient.instance.register(req).enqueue(object : Callback<RegisterResponse> {
                override fun onResponse(call: Call<RegisterResponse>, response: Response<RegisterResponse>) {
                    val res = response.body()

                    if (res != null) {

                        getSharedPreferences("app", MODE_PRIVATE)
                            .edit()
                            .putString("email", email)
                            .apply()

                        startActivity(Intent(this@RegisterActivity, ChatActivity::class.java))
                        finish()
                    }
                }

                override fun onFailure(call: Call<RegisterResponse>, t: Throwable) {
                    Toast.makeText(this@RegisterActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }
    }
}
