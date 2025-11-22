# Android App Debugging Guide

## Filtering Logcat for Your App

### In Android Studio Logcat:

1. **Filter by Package Name:**
   - In the logcat filter box, type: `package:com.example.mentalhealthchat`

2. **Filter by Tag:**
   - If you're using OkHttp/Retrofit, filter by: `OkHttp` or `Retrofit`
   - For general HTTP: `HttpURLConnection` or `Volley`

3. **Filter by Log Level:**
   - Show only errors: `level:error`
   - Show errors and warnings: `level:warning`

4. **Combined Filter:**
   ```
   package:com.example.mentalhealthchat level:error
   ```

## What to Look For

### ✅ Good Signs:
- HTTP 200 responses
- Successful API calls
- JSON parsing working

### ❌ Problem Signs:
- `SocketTimeoutException` - Server not responding
- `UnknownHostException` - Can't reach server (wrong URL)
- `Connection refused` - Server not running
- HTTP 400/500 errors - API errors
- `SSLException` - HTTPS/SSL issues
- `JsonSyntaxException` - JSON parsing errors

## Common Issues & Solutions

### 1. **Can't Connect to Server**
```
UnknownHostException: Unable to resolve host "localhost"
```
**Solution:** Use `10.0.2.2` instead of `localhost` for Android Emulator
- Local server: `http://10.0.2.2:5001/chat`
- Real device: Use your computer's IP: `http://192.168.x.x:5001/chat`

### 2. **Connection Refused**
```
java.net.ConnectException: Connection refused
```
**Solution:** 
- Make sure Python server is running
- Check firewall isn't blocking port 5001
- Verify server is listening on `0.0.0.0` not `127.0.0.1`

### 3. **Network Security Config (Android 9+)**
If using HTTP (not HTTPS), add to `AndroidManifest.xml`:
```xml
<application
    android:usesCleartextTraffic="true"
    ...>
```

### 4. **Main Thread Blocking**
```
Skipped 103 frames! The application may be doing too much work on its main thread.
```
**Solution:** Make API calls on background thread (use AsyncTask, Coroutines, or RxJava)

## Adding Logging to Your Android App

### If using OkHttp:
```kotlin
val loggingInterceptor = HttpLoggingInterceptor()
loggingInterceptor.level = HttpLoggingInterceptor.Level.BODY
```

### If using Retrofit:
```kotlin
val client = OkHttpClient.Builder()
    .addInterceptor(HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    })
    .build()
```

### Manual Logging:
```kotlin
Log.d("API", "Request: $requestBody")
Log.d("API", "Response: $responseBody")
Log.e("API", "Error: ${e.message}", e)
```

## Testing Steps

1. **Check if server is reachable:**
   ```kotlin
   // Test in browser or Postman first
   // Then test from Android app
   ```

2. **Verify URL:**
   - Emulator: `http://10.0.2.2:5001/chat`
   - Real device: `http://YOUR_COMPUTER_IP:5001/chat`

3. **Check permissions:**
   ```xml
   <uses-permission android:name="android.permission.INTERNET" />
   ```

4. **Test with simple request:**
   ```kotlin
   // First test health endpoint
   GET http://10.0.2.2:5001/health
   ```

## Getting Your Computer's IP (for real device)

**Windows:**
```powershell
ipconfig
# Look for IPv4 Address under your network adapter
```

**Mac/Linux:**
```bash
ifconfig
# or
ip addr show
```



