// Simpler version - just display topics in a TextView or Log

package com.example.mentalhealthchat.ui

import android.util.Log
import android.widget.TextView
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.*
import org.json.JSONArray
import org.json.JSONObject

class MainActivity : AppCompatActivity() {
    
    private val BASE_URL = "http://10.0.2.2:5001"
    private val client = OkHttpClient()
    
    // Add this method to your MainActivity
    fun loadTopics() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val url = "$BASE_URL/topics"
                val request = Request.Builder()
                    .url(url)
                    .get()
                    .build()
                
                val response = client.newCall(request).execute()
                val responseBody = response.body?.string() ?: ""
                
                if (response.isSuccessful) {
                    val json = JSONObject(responseBody)
                    val totalSections = json.getInt("total_sections")
                    val topicsArray = json.getJSONArray("topics")
                    
                    Log.d("Topics", "Total sections: $totalSections")
                    
                    val topicsList = StringBuilder()
                    topicsList.append("Indexed Topics:\n\n")
                    
                    for (i in 0 until topicsArray.length()) {
                        val topic = topicsArray.getJSONObject(i)
                        val source = topic.getString("source")
                        val topics = topic.getJSONArray("topics")
                        
                        topicsList.append("${i + 1}. Source: $source\n")
                        topicsList.append("   Topics: ")
                        
                        for (j in 0 until topics.length()) {
                            topicsList.append(topics.getString(j))
                            if (j < topics.length() - 1) topicsList.append(", ")
                        }
                        topicsList.append("\n\n")
                    }
                    
                    // Display in TextView or Log
                    withContext(Dispatchers.Main) {
                        // If you have a TextView:
                        // topicsTextView.text = topicsList.toString()
                        
                        // Or just log it:
                        Log.d("Topics", topicsList.toString())
                    }
                }
            } catch (e: Exception) {
                Log.e("Topics", "Error loading topics", e)
            }
        }
    }
    
    // Call this in onCreate() or when you want to show topics
    // loadTopics()
}



