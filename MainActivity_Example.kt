// Example MainActivity.kt with proper API calling and debugging
// Replace your MainActivity with this or use it as reference

package com.example.mentalhealthchat.ui

import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

class MainActivity : AppCompatActivity() {
    
    // IMPORTANT: Use 10.0.2.2 for emulator, or your computer's IP for real device
    private val BASE_URL = "http://10.0.2.2:5001"  // Change this!
    
    private lateinit var messageEditText: EditText
    private lateinit var sendButton: Button
    private lateinit var responseTextView: TextView
    
    private val client = OkHttpClient()
    
    companion object {
        private const val TAG = "MainActivity"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize views (adjust IDs based on your layout)
        // messageEditText = findViewById(R.id.messageEditText)
        // sendButton = findViewById(R.id.sendButton)
        // responseTextView = findViewById(R.id.responseTextView)
        
        // Set click listener
        // sendButton.setOnClickListener {
        //     sendMessage()
        // }
    }
    
    private fun sendMessage() {
        val message = messageEditText.text.toString().trim()
        
        if (message.isEmpty()) {
            Log.w(TAG, "Message is empty")
            return
        }
        
        Log.d(TAG, "Sending message: $message")
        
        // Run on background thread
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = makeApiCall(message)
                withContext(Dispatchers.Main) {
                    displayResponse(response)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error making API call", e)
                withContext(Dispatchers.Main) {
                    responseTextView.text = "Error: ${e.message}"
                }
            }
        }
    }
    
    private suspend fun makeApiCall(message: String): String {
        return withContext(Dispatchers.IO) {
            val url = "$BASE_URL/chat"
            Log.d(TAG, "API URL: $url")
            
            // Create JSON request body
            val json = JSONObject()
            json.put("message", message)
            val requestBody = json.toString()
                .toRequestBody("application/json".toMediaType())
            
            Log.d(TAG, "Request body: $requestBody")
            
            // Create request
            val request = Request.Builder()
                .url(url)
                .post(requestBody)
                .addHeader("Content-Type", "application/json")
                .build()
            
            // Make the call
            try {
                val response = client.newCall(request).execute()
                val responseBody = response.body?.string() ?: ""
                
                Log.d(TAG, "Response code: ${response.code}")
                Log.d(TAG, "Response body: $responseBody")
                
                if (!response.isSuccessful) {
                    throw IOException("Unexpected code $response: $responseBody")
                }
                
                // Parse JSON response
                val jsonResponse = JSONObject(responseBody)
                val reply = jsonResponse.getString("reply")
                
                Log.d(TAG, "Parsed reply: $reply")
                
                reply
            } catch (e: IOException) {
                Log.e(TAG, "Network error", e)
                throw Exception("Network error: ${e.message}")
            } catch (e: Exception) {
                Log.e(TAG, "Error parsing response", e)
                throw Exception("Error: ${e.message}")
            }
        }
    }
    
    private fun displayResponse(response: String) {
        // Replace \n with actual newlines for display
        val formattedResponse = response.replace("\\n", "\n")
        responseTextView.text = formattedResponse
        Log.d(TAG, "Displayed response to user")
    }
    
    // Test health endpoint (call this first to verify connection)
    private fun testHealthEndpoint() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val url = "$BASE_URL/health"
                val request = Request.Builder()
                    .url(url)
                    .get()
                    .build()
                
                val response = client.newCall(request).execute()
                val responseBody = response.body?.string() ?: ""
                
                Log.d(TAG, "Health check response: $responseBody")
                
                withContext(Dispatchers.Main) {
                    responseTextView.text = "Health: $responseBody"
                }
            } catch (e: Exception) {
                Log.e(TAG, "Health check failed", e)
            }
        }
    }
}



