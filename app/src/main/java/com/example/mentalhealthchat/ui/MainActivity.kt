package com.example.mentalhealthchat.com.example.mentalhealthchat.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.Text
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import com.example.mentalhealthchat.ui.theme.MentalHealthChatTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MentalHealthChatTheme {
                GreetingScreen()
            }
        }
    }
}

@Composable
fun GreetingScreen() {
    Text(
        text = "Hello from Mental Health Chat App!",
        style = MaterialTheme.typography.titleLarge
    )
}
