package com.example.mentalhealthchat.ui

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

data class RegisterRequest(
    val email: String,
    val age: Int,
    val sex: String
)

data class RegisterResponse(
    val status: String,
    val message: String,
    val usage_count: Int
)

data class ChatRequest(
    val email: String,
    val message: String
)

data class ChatResponse(
    val allowed: Boolean,
    val reply: String?,
    val usage_now: Int?,
    val limit: Int?,
    val error: String?
)

interface ApiService {

    @POST("auth/register")
    fun register(@Body req: RegisterRequest): Call<RegisterResponse>

    @POST("chat")
    fun chat(@Body req: ChatRequest): Call<ChatResponse>
}
