// Example code to fetch and display indexed topics in Android app

package com.example.mentalhealthchat.ui

import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.*
import org.json.JSONArray
import org.json.JSONObject

class TopicsActivity : AppCompatActivity() {
    
    private val BASE_URL = "http://10.0.2.2:5001"  // Change for your setup
    private val client = OkHttpClient()
    
    private lateinit var topicsRecyclerView: RecyclerView
    private lateinit var totalSectionsTextView: TextView
    private lateinit var refreshButton: Button
    
    companion object {
        private const val TAG = "TopicsActivity"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(R.layout.activity_topics)  // Your layout
        
        // Initialize views
        // topicsRecyclerView = findViewById(R.id.topicsRecyclerView)
        // totalSectionsTextView = findViewById(R.id.totalSectionsTextView)
        // refreshButton = findViewById(R.id.refreshButton)
        
        // Setup RecyclerView
        topicsRecyclerView.layoutManager = LinearLayoutManager(this)
        
        // Fetch topics on create
        fetchTopics()
        
        // Refresh button
        // refreshButton.setOnClickListener {
        //     fetchTopics()
        // }
    }
    
    private fun fetchTopics() {
        Log.d(TAG, "Fetching indexed topics...")
        
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val topicsData = getTopicsFromAPI()
                withContext(Dispatchers.Main) {
                    displayTopics(topicsData)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error fetching topics", e)
                withContext(Dispatchers.Main) {
                    // Show error message
                    totalSectionsTextView.text = "Error: ${e.message}"
                }
            }
        }
    }
    
    private suspend fun getTopicsFromAPI(): TopicsData {
        return withContext(Dispatchers.IO) {
            val url = "$BASE_URL/topics"
            Log.d(TAG, "Fetching from: $url")
            
            val request = Request.Builder()
                .url(url)
                .get()
                .build()
            
            val response = client.newCall(request).execute()
            val responseBody = response.body?.string() ?: ""
            
            Log.d(TAG, "Response: $responseBody")
            
            if (!response.isSuccessful) {
                throw Exception("Failed to fetch topics: ${response.code}")
            }
            
            val json = JSONObject(responseBody)
            val totalSections = json.getInt("total_sections")
            val topicsArray = json.getJSONArray("topics")
            
            val topics = mutableListOf<TopicInfo>()
            for (i in 0 until topicsArray.length()) {
                val topicObj = topicsArray.getJSONObject(i)
                topics.add(
                    TopicInfo(
                        id = topicObj.getString("id"),
                        source = topicObj.getString("source"),
                        topics = jsonArrayToList(topicObj.getJSONArray("topics")),
                        preview = topicObj.getString("preview")
                    )
                )
            }
            
            TopicsData(totalSections, topics)
        }
    }
    
    private fun jsonArrayToList(jsonArray: JSONArray): List<String> {
        val list = mutableListOf<String>()
        for (i in 0 until jsonArray.length()) {
            list.add(jsonArray.getString(i))
        }
        return list
    }
    
    private fun displayTopics(data: TopicsData) {
        totalSectionsTextView.text = "Total Sections: ${data.totalSections}"
        
        // Set adapter for RecyclerView
        val adapter = TopicsAdapter(data.topics)
        topicsRecyclerView.adapter = adapter
        
        Log.d(TAG, "Displayed ${data.topics.size} topics")
    }
    
    // Data classes
    data class TopicsData(
        val totalSections: Int,
        val topics: List<TopicInfo>
    )
    
    data class TopicInfo(
        val id: String,
        val source: String,
        val topics: List<String>,
        val preview: String
    )
}

// RecyclerView Adapter
class TopicsAdapter(private val topics: List<TopicsActivity.TopicInfo>) :
    RecyclerView.Adapter<TopicsAdapter.TopicViewHolder>() {
    
    class TopicViewHolder(val textView: TextView) : RecyclerView.ViewHolder(textView)
    
    override fun onCreateViewHolder(parent: android.view.ViewGroup, viewType: Int): TopicViewHolder {
        val textView = TextView(parent.context)
        textView.setPadding(16, 16, 16, 16)
        textView.textSize = 14f
        return TopicViewHolder(textView)
    }
    
    override fun onBindViewHolder(holder: TopicViewHolder, position: Int) {
        val topic = topics[position]
        val topicsStr = topic.topics.joinToString(", ")
        holder.textView.text = """
            Source: ${topic.source}
            Topics: $topicsStr
            Preview: ${topic.preview}
        """.trimIndent()
    }
    
    override fun getItemCount() = topics.size
}



