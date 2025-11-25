# Android App Debugging Steps

## Step 1: Check MainActivity.kt/Java

Open `MainActivity.kt` (or `.java`) and look for:
- API endpoint URL
- HTTP client setup (OkHttp, Retrofit, Volley, etc.)
- Error handling
- Logging statements

## Step 2: Add Logging to Your API Calls

### If using OkHttp/Retrofit:

```kotlin
// Add this to your build.gradle (Module: app)
dependencies {
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
}

// In your API setup code:
val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = HttpLoggingInterceptor.Level.BODY
}

val client = OkHttpClient.Builder()
    .addInterceptor(loggingInterceptor)
    .build()
```

### Manual Logging (add to your API call code):

```kotlin
Log.d("API_DEBUG", "URL: $url")
Log.d("API_DEBUG", "Request: $requestBody")
Log.d("API_DEBUG", "Response Code: ${response.code()}")
Log.d("API_DEBUG", "Response Body: ${response.body()?.string()}")
```

## Step 3: Check AndroidManifest.xml

Make sure you have:

```xml
<uses-permission android:name="android.permission.INTERNET" />

<application
    android:usesCleartextTraffic="true"  <!-- Needed for HTTP (not HTTPS) -->
    ...>
```

## Step 4: Verify API URL

### For Android Emulator:
```kotlin
val BASE_URL = "http://10.0.2.2:5001"  // NOT localhost!
```

### For Real Device:
```kotlin
val BASE_URL = "http://192.168.x.x:5001"  // Your computer's IP
```

## Step 5: Test Health Endpoint First

Before testing chat, test the health endpoint:

```kotlin
// Simple test
val url = "http://10.0.2.2:5001/health"
// Make GET request and log response
```

## Step 6: Filter Logcat

In Android Studio Logcat:
1. Filter by: `package:com.example.mentalhealthchat`
2. Search for: `API_DEBUG` or `OkHttp` or `HTTP`
3. Look for errors: `level:error`

## Step 7: Common Issues Checklist

- [ ] Internet permission in AndroidManifest.xml
- [ ] `usesCleartextTraffic="true"` for HTTP
- [ ] Using `10.0.2.2` not `localhost` (emulator)
- [ ] Python server is running
- [ ] Firewall not blocking port 5001
- [ ] API calls on background thread (not main thread)



