# Voice Assistant - Comprehensive Voice-Controlled AI Assistant

A sophisticated Python-based voice assistant that can perform a wide variety of tasks through voice commands. This assistant uses speech recognition to understand your commands and text-to-speech to respond, making it a fully voice-interactive experience.

## Features

### 🎤 **Core Voice Features**
- **Speech Recognition**: Listens to voice commands using Google Speech Recognition API
- **Text-to-Speech**: Responds vocally using pyttsx3 (SAPI5 on Windows)
- **Greeting System**: Personalized greetings based on time of day (Good Morning/Afternoon/Evening)

### 🌐 **Web Browsing & Search**
- **Wikipedia Search**: Search and get summaries from Wikipedia
  - Command: "search wikipedia [topic]" or "wikipedia [topic]"
  - Example: "wikipedia artificial intelligence"
  
- **Web Search**: Search the web using Google, Bing, or DuckDuckGo
  - Command: "search web for [query]"
  - Example: "search web for Python tutorials"
  
- **Website Navigation**: Open specific websites
  - Commands: "open youtube", "open google", "play music"
  - Custom: "open website [website.com]"
  
- **YouTube Music**: Opens YouTube Music for streaming

### 🌤️ **Weather & News**
- **Weather Information**: Get current weather for any city
  - Command: "weather in [city name]"
  - Example: "weather in New York"
  - Provides: Temperature, feels-like temperature, weather description, humidity
  
- **News Headlines**: Get top news headlines from major sources
  - Commands: "tell me the news" or "what's in the news"
  - Reads top 5 headlines

### ⏰ **Time Management**
- **Current Time**: Get the current time
  - Command: "the time"
  
- **Reminders**: Set reminders with time delays
  - Command: "set reminder for [X minutes/seconds]"
  - Example: "set reminder for 5 minutes"
  - Assistant will prompt for reminder text if not provided
  
- **Scheduled Tasks**: Schedule tasks for specific times
  - Command: "schedule task [task description]"
  - Example: "schedule task call mom"

### 🧮 **Calculations & Conversions**
- **Mathematical Calculations**: Perform complex calculations
  - Command: "calculate [expression]"
  - Examples: 
    - "calculate 15 * 23"
    - "calculate 100 + 50 - 25"
    - "calculate 10 to the power of 3"
  
- **Unit Conversions**: Convert between different units
  - Command: "convert [value] [from_unit] to [to_unit]"
  - Supported conversions:
    - **Length**: meters, kilometers, centimeters, millimeters, inches, feet, yards, miles
    - **Weight**: grams, kilograms, milligrams, pounds, ounces
    - **Temperature**: Celsius, Fahrenheit, Kelvin
  - Examples:
    - "convert 10 meters to feet"
    - "convert 100 pounds to kilograms"
    - "convert 32 fahrenheit to celsius"

### 💻 **System Control**
- **System Information**: Monitor system resources
  - Commands: "system info" or "system status"
  - Provides: CPU usage percentage, memory usage percentage, battery level
  
- **Application Launcher**: Open system applications
  - Commands:
    - "open notepad"
    - "open calculator"
    - "open command prompt" (Windows) / "open terminal" (Mac/Linux)
  
- **Screenshot**: Capture and save screenshots
  - Command: "take screenshot"
  - Saves with timestamp: `screenshot_YYYYMMDD_HHMMSS.png`
  
- **System Power Control**: Shutdown or restart system (with confirmation)
  - Commands: "shutdown" or "restart"
  - Requires voice confirmation before executing

### 📁 **File Management**
- **File Search**: Search for files by name/keyword
  - Command: "search files for [keyword]"
  - Example: "search files for document"
  - Searches home directory by default, shows up to 10 results
  
- **Open Files**: Open files with default applications
  - Command: "open file [filename]"
  - Automatically searches common directories (Downloads, Documents, Music, Pictures)
  
- **Directory Listing**: List contents of directories
  - Command: "list directory [path]"
  - If no path specified, lists current directory
  - Reads first 10 items

### 🏠 **Smart Home Automation** (Optional)
- **Philips Hue Integration**: Control smart lights
  - Commands:
    - "turn on [light name]" (e.g., "turn on living room light")
    - "turn off [light name]"
    - "set brightness [light name] to [0-255]"
  - Requires: phue module and Philips Hue bridge configuration

### 😄 **Entertainment**
- **Jokes**: Tell random jokes
  - Command: "tell me a joke"
  
- **Inspirational Quotes**: Share motivational quotes
  - Commands: "tell me a quote" or "inspire me"
  - Features quotes from Steve Jobs, Eleanor Roosevelt, and more

## Installation

### Prerequisites
- Python 3.6 or higher
- Microphone connected to your computer
- Internet connection (for speech recognition and web features)

### Step 1: Install Python Dependencies

Install all required packages using pip:

```bash
pip install -r requirements.txt
```

Or install manually:

**Core Dependencies:**
```bash
pip install pyttsx3
pip install SpeechRecognition
pip install pyautogui
pip install wikipedia
pip install requests
pip install psutil
```

**Optional Dependencies (for enhanced features):**
```bash
pip install phue  # For Philips Hue smart home control
```

### Step 2: Install Additional System Dependencies

#### Windows:
- No additional setup needed for most features
- Windows SAPI5 voices are included by default

#### Linux:
- Install PyAudio dependencies:
  ```bash
  sudo apt-get install portaudio19-dev python3-pyaudio
  ```

#### macOS:
- Install PyAudio:
  ```bash
  brew install portaudio
  pip install pyaudio
  ```

### Step 3: Configure API Keys (Optional but Recommended)

The assistant includes default API keys, but you can configure your own for better service:

**Option A: Environment Variables**
```bash
# Windows (PowerShell)
$env:WEATHER_API_KEY="your_openweathermap_api_key"
$env:NEWS_API_KEY="your_newsapi_key"

# Linux/macOS
export WEATHER_API_KEY="your_openweathermap_api_key"
export NEWS_API_KEY="your_newsapi_key"
```

**Option B: Create config.py** (Optional)
Create a `config.py` file in the same directory:
```python
WEATHER_API_KEY = "your_openweathermap_api_key"
NEWS_API_KEY = "your_newsapi_key"
ASSISTANT_NAME = "Jarvis"  # Customize assistant name

# Smart Home Configuration
SMART_HOME_CONFIG = {
    "philips_hue": {
        "enabled": True,
        "bridge_ip": "192.168.1.100"  # Your Hue bridge IP
    },
    "devices": {
        "living_room_light": {"type": "light", "id": 1},
        "bedroom_light": {"type": "light", "id": 2},
        "kitchen_light": {"type": "light", "id": 3}
    }
}

# File Management Configuration
FILE_MANAGEMENT_CONFIG = {
    "downloads_path": "C:/Users/YourName/Downloads",
    "documents_path": "C:/Users/YourName/Documents",
    "music_path": "C:/Users/YourName/Music",
    "pictures_path": "C:/Users/YourName/Pictures"
}
```

**Get API Keys:**
- **OpenWeatherMap**: Sign up at https://openweathermap.org/api (Free tier available)
- **NewsAPI**: Sign up at https://newsapi.org (Free tier available)

## Usage

### Running the Assistant

Simply run the Python script:

```bash
python voice_assistant_improved.py
```

Or on some systems:

```bash
python3 voice_assistant_improved.py
```

### Using Voice Commands

1. **Start the assistant**: Run the script and wait for the greeting
2. **Speak clearly**: When you see "Listening..." speak your command
3. **Wait for response**: The assistant will process and respond
4. **Continue**: The assistant stays active and waits for your next command
5. **Exit**: Say "exit" or "quit" to stop the assistant

### Example Interaction

```
Assistant: Good Morning!
Assistant: I am your voice assistant. Please tell me how may I help you

You: "What's the weather in London?"
Assistant: The temperature in London is 18 degrees Celsius, feels like 17 degrees, 
          with clear sky and humidity is 65 percent

You: "Tell me a joke"
Assistant: Why don't scientists trust atoms? Because they make up everything!

You: "Calculate 25 times 17"
Assistant: The result is 425

You: "Open YouTube"
Assistant: Opening YouTube

You: "Exit"
Assistant: Goodbye! Have a great day!
```

## Voice Command Reference

### Quick Command List

| Category | Command Examples |
|----------|-----------------|
| **Web & Search** | "wikipedia AI", "search web for Python", "open youtube", "open google" |
| **Weather & News** | "weather in Paris", "tell me the news" |
| **Time** | "the time", "set reminder for 10 minutes" |
| **Calculations** | "calculate 15 + 23", "convert 50 miles to kilometers" |
| **System** | "system info", "open notepad", "take screenshot" |
| **Files** | "search files for document", "open file readme.txt" |
| **Entertainment** | "tell me a joke", "inspire me" |
| **Smart Home** | "turn on living room light", "set brightness bedroom light to 150" |
| **Control** | "exit", "quit", "shutdown", "restart" |

## Troubleshooting

### Speech Recognition Issues

**Problem**: "Could not understand audio" or recognition not working
- **Solution**: 
  - Ensure microphone is connected and working
  - Check microphone permissions in system settings
  - Speak clearly and reduce background noise
  - Ensure internet connection is active (Google Speech Recognition requires internet)

### Text-to-Speech Issues

**Problem**: Assistant not speaking
- **Solution**:
  - Check if pyttsx3 is installed: `pip install pyttsx3`
  - On Windows, ensure SAPI5 voices are available
  - Assistant will print responses if TTS fails

### Module Import Errors

**Problem**: "Module not available" errors
- **Solution**:
  - Install missing modules: `pip install [module_name]`
  - Some features are optional and will be disabled if modules aren't available
  - The assistant will still function with core features

### Weather/News API Errors

**Problem**: Weather or news features not working
- **Solution**:
  - Check internet connection
  - Verify API keys are set correctly
  - Free API tiers may have rate limits

### Microphone Not Found

**Problem**: "Microphone not found" error
- **Solution**:
  - Ensure microphone is connected
  - Check system audio settings
  - On Linux, may need to configure audio devices

## Advanced Configuration

### Customizing Voice Settings

The assistant uses the default SAPI5 voice on Windows. To customize:

1. Edit the `speak()` function initialization
2. Adjust voice properties:
   ```python
   engine.setProperty('rate', 150)  # Speech rate (words per minute)
   engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
   ```

### Adjusting Speech Recognition Sensitivity

Edit the `takecommand()` function:
```python
r.energy_threshold = 300  # Lower = more sensitive
r.pause_threshold = 1     # Seconds of silence before processing
```

## Safety & Privacy

- **Speech Recognition**: Uses Google Speech Recognition API (requires internet)
- **Voice Data**: Audio is processed by Google's service
- **API Keys**: Store securely; consider using environment variables
- **System Commands**: Shutdown/restart commands require confirmation
- **File Access**: Only accesses files you explicitly request

## Limitations

1. **Internet Required**: Speech recognition and web features need internet
2. **Language**: Currently optimized for English (en-US)
3. **Accuracy**: Voice recognition depends on microphone quality and background noise
4. **Platform**: Some features are platform-specific (Windows/Mac/Linux)
5. **API Rate Limits**: Free API tiers may have usage limits

## Contributing

Feel free to enhance the assistant with:
- Additional voice commands
- More integrations (smart home devices, services)
- Improved natural language processing
- Multi-language support
- Offline speech recognition

## License

This project is open source and available for personal and educational use.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all dependencies are installed
3. Check Python version compatibility (3.6+)
4. Review error messages in the console output

## Feature Summary

### ✅ Fully Functional Features
- Voice recognition and text-to-speech
- Wikipedia search
- Web browsing and search
- Weather information
- News headlines
- Time queries
- Reminders and scheduling
- Mathematical calculations
- Unit conversions
- System information monitoring
- Application launching
- Screenshots
- File search and management
- Jokes and quotes
- System power control

### ⚙️ Optional Features (Require Additional Setup)
- Smart home automation (Philips Hue)
- Custom API keys for weather/news
- Custom file paths configuration

---

**Enjoy your voice assistant!** 🎤✨

For the best experience, speak clearly and use natural commands. The assistant learns from your usage patterns and works best in a quiet environment.

