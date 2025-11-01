# Core required modules with error handling
try:
    import pyttsx3
    tts_available = True
except ImportError:
    print("pyttsx3 module not available. Text-to-speech will be disabled.")
    tts_available = False
    pyttsx3 = None

try:
    import speech_recognition as sr
    sr_available = True
except ImportError:
    print("speech_recognition module not available. Voice recognition will be disabled.")
    sr_available = False
    sr = None

# Standard library modules
import pyautogui
import time
import datetime
import wikipedia
import webbrowser
import os
import random
import subprocess
import sys
import re
import json
import ast
import operator
from collections import deque
from typing import Any, List, Union
from urllib.parse import quote_plus

# Conditional imports for optional features
try:
    import requests
    requests_available = True
except ImportError:
    requests_available = False
    print("Requests module not available. Weather and news features will be disabled.")
    requests = None

try:
    import psutil
    psutil_available = True
except ImportError:
    psutil_available = False
    print("Psutil module not available. System monitoring features will be disabled.")
    psutil = None

# Smart home automation modules (optional)
try:
    import phue  # For Philips Hue lights
    phue_available = True
except ImportError:
    phue_available = False
    print("phue module not available. Philips Hue control will be disabled.")
    phue = None

# Initialize text-to-speech engine
engine = None
if tts_available and pyttsx3:
    try:
        engine = pyttsx3.init('sapi5')
        voices: Union[List[Any], Any] = engine.getProperty('voices')
        # Handle voices more safely with proper type checking
        try:
            # Check if voices is a list-like object before accessing
            if isinstance(voices, (list, tuple)) and len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            elif isinstance(voices, (list, tuple)) and len(voices) > 0:
                engine.setProperty('voice', voices[0].id)
        except (TypeError, AttributeError, IndexError) as e:
            # Fallback to default voice if there's any issue
            print(f"Warning: Could not set voice: {e}")
            pass
    except Exception as e:
        print(f"Error initializing text-to-speech engine: {e}")
        engine = None
        tts_available = False

# Global variables for enhanced functionality
reminders = deque()
scheduled_tasks = []

# Import configuration
try:
    from config import WEATHER_API_KEY, NEWS_API_KEY, SMART_HOME_CONFIG, FILE_MANAGEMENT_CONFIG
    weather_api_key = WEATHER_API_KEY or os.environ.get("WEATHER_API_KEY") or "4b5f802e3151b0e49313f5679ce5fd85"
    news_api_key = NEWS_API_KEY or os.environ.get("NEWS_API_KEY") or "FEpt_YhuQtJ0nOWO3k_x0EeguhCEHYqH"
    smart_home_config = SMART_HOME_CONFIG
    file_management_config = FILE_MANAGEMENT_CONFIG
except ImportError:
    # Fallback to environment variables if config file is not available
    weather_api_key = os.environ.get("WEATHER_API_KEY") or "4b5f802e3151b0e49313f5679ce5fd85"
    news_api_key = os.environ.get("NEWS_API_KEY") or "FEpt_YhuQtJ0nOWO3k_x0EeguhCEHYqH"
    
    # Smart home configuration
    smart_home_config = {
        "philips_hue": {
            "enabled": False,
            "bridge_ip": "192.168.1.100",  # Default IP, change as needed
            "bridge": None
        },
        "devices": {
            "living_room_light": {"type": "light", "id": 1},
            "bedroom_light": {"type": "light", "id": 2},
            "kitchen_light": {"type": "light", "id": 3}
        }
    }
    
    # File management configuration
    file_management_config = {
        "downloads_path": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents_path": os.path.join(os.path.expanduser("~"), "Documents"),
        "music_path": os.path.join(os.path.expanduser("~"), "Music"),
        "pictures_path": os.path.join(os.path.expanduser("~"), "Pictures")
    }

# Ensure API keys are set (final fallback)
if not weather_api_key:
    weather_api_key = "4b5f802e3151b0e49313f5679ce5fd85"
if not news_api_key:
    news_api_key = "FEpt_YhuQtJ0nOWO3k_x0EeguhCEHYqH"

def speak(audio):
    """Speak the given text using TTS or print if TTS unavailable"""
    # Always print to console for debugging
    print(f"Assistant: {audio}")
    if engine and tts_available:
        try:
            engine.say(audio)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
            # Continue - we already printed to console
    else:
        # TTS not available, message already printed above
        pass

def wishMe():
    """Greet the user based on time of day"""
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")

    # Try to get assistant name from config, fallback to default
    try:
        from config import ASSISTANT_NAME
        assistant_name = ASSISTANT_NAME
    except ImportError:
        assistant_name = "your voice assistant"
    
    speak(f"I am {assistant_name}. Please tell me how may I help you")

def takecommand():
    """Listen for voice commands and return recognized text"""
    if not sr_available or not sr:
        print("Voice recognition not available. Please install speech_recognition module.")
        return "none"
        
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        r.energy_threshold = 300
        r.dynamic_energy_threshold = False
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        # Direct method call with exception handling
        # Type ignore comment to suppress linter warning
        query = r.recognize_google(audio, language='en-US')  # type: ignore
        print(f"User said: {query}\n")
        return query.lower()

    except sr.UnknownValueError:
        print("Could not understand audio. Say that again please...")
        return "none"
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return "none"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "none"

def get_weather(city):
    """Get weather information for a specified city"""
    if not requests_available or not requests:
        speak("Weather feature is not available. Please install the requests module.")
        return
        
    if not weather_api_key:
        speak("Weather API key not configured. Please set the WEATHER_API_KEY environment variable.")
        return
        
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        
        # Check response code - OpenWeatherMap returns cod as int or string
        cod = weather_data.get("cod")
        if cod != "404" and cod != 404:
            main = weather_data["main"]
            temperature = main["temp"]
            humidity = main["humidity"]
            weather_desc = weather_data["weather"][0]["description"]
            feels_like = main.get("feels_like", temperature)
            speak(f"The temperature in {city} is {temperature} degrees Celsius, feels like {feels_like} degrees, with {weather_desc} and humidity is {humidity} percent")
        else:
            speak("City not found")
    except requests.exceptions.Timeout:
        speak("The weather request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        speak("Sorry, I couldn't fetch the weather information")
        print(f"Weather API error: {e}")
    except Exception as e:
        speak("Sorry, I couldn't fetch the weather information")
        print(f"Unexpected error: {e}")

def get_news():
    """Get top news headlines"""
    if not requests_available or not requests:
        speak("News feature is not available. Please install the requests module.")
        return
        
    if not news_api_key:
        speak("News API key not configured. Please set the NEWS_API_KEY environment variable.")
        return
        
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        news_data = response.json()
        
        # Check if articles exist in response
        articles = news_data.get("articles", [])
        if articles:
            speak("Here are the top news headlines")
            for i, article in enumerate(articles[:5]):
                title = article.get('title', 'No title available')
                speak(f"News {i+1}: {title}")
        else:
            speak("Sorry, no news articles found at the moment")
    except requests.exceptions.Timeout:
        speak("The news request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        speak("Sorry, I couldn't fetch the news at the moment")
        print(f"News API error: {e}")
    except Exception as e:
        speak("Sorry, I couldn't fetch the news at the moment")
        print(f"Unexpected error: {e}")

def set_reminder(reminder_text, time_delay):
    """Set a reminder for a specified time delay"""
    reminder_time = datetime.datetime.now() + datetime.timedelta(seconds=time_delay)
    reminders.append((reminder_text, reminder_time))
    speak(f"Reminder set for {time_delay} seconds from now")

def check_reminders():
    """Check and announce any due reminders"""
    current_time = datetime.datetime.now()
    while reminders and reminders[0][1] <= current_time:
        reminder_text, reminder_time = reminders.popleft()
        speak(f"Reminder: {reminder_text}")

def schedule_task(task_description, scheduled_time):
    """Schedule a task for a specific time"""
    scheduled_tasks.append({
        "task": task_description,
        "time": scheduled_time
    })
    speak(f"Task scheduled for {scheduled_time.strftime('%H:%M')}")

def check_scheduled_tasks():
    """Check and execute scheduled tasks"""
    current_time = datetime.datetime.now()
    for task in scheduled_tasks[:]:  # Use slice copy to avoid modification during iteration
        if task["time"] <= current_time:
            speak(f"Scheduled task: {task['task']}")
            scheduled_tasks.remove(task)

def get_system_info():
    """Get system information including CPU, memory, and battery"""
    if not psutil_available or not psutil:
        speak("System monitoring feature is not available. Please install the psutil module.")
        return
        
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        battery = psutil.sensors_battery()
        battery_percent = battery.percent if battery else "Unknown"
        
        speak(f"CPU usage is {cpu_usage} percent, Memory usage is {memory_percent} percent, Battery level is {battery_percent} percent")
    except Exception as e:
        speak("Sorry, I couldn't fetch system information")
        print(f"System info error: {e}")

def tell_joke():
    """Tell a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What did one ocean say to the other ocean? Nothing, they just waved!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call a fake noodle? An impasta!",
        "How does a penguin build its house? Igloos it together!"
    ]
    speak(random.choice(jokes))

def tell_quote():
    """Tell a random inspirational quote"""
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
        "Stay hungry, stay foolish. - Steve Jobs",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt"
    ]
    speak(random.choice(quotes))

def safe_calculate(expression):
    """Safely evaluate mathematical expressions without using eval()"""
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }
    
    def eval_expr(node):
        # ast.Constant is used in Python 3.8+, ast.Num was deprecated and removed in Python 3.14
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](eval_expr(node.operand))
        else:
            raise TypeError(f"Unsupported operation: {type(node)}")
    
    try:
        tree = ast.parse(expression, mode='eval')
        result = eval_expr(tree.body)
        return result
    except Exception:
        raise ValueError("Invalid mathematical expression")

def calculate(expression):
    """Calculate mathematical expressions safely"""
    try:
        # Replace common words with operators
        expression = expression.replace("plus", "+")
        expression = expression.replace("minus", "-")
        expression = expression.replace("times", "*")
        expression = expression.replace("multiply", "*")
        expression = expression.replace("divided by", "/")
        expression = expression.replace("divide", "/")
        expression = expression.replace("to the power of", "**")
        expression = expression.replace("power", "**")
        
        # Remove letters but keep operators, numbers, and spaces
        # Operators: + - * / ** ( )
        expression = re.sub(r'[a-zA-Z]', '', expression)
        # Remove spaces to clean up expression
        expression = expression.replace(" ", "")
        expression = expression.strip()
        
        if not expression:
            speak("Please provide a mathematical expression to calculate")
            return
        
        # Handle single number
        if expression.isdigit() or (expression.startswith('-') and expression[1:].replace('.', '').isdigit()):
            result = float(expression)
            speak(f"The result is {result}")
            return
            
        result = safe_calculate(expression)
        speak(f"The result is {result}")
    except Exception as e:
        speak("Sorry, I couldn't calculate that. Please provide a valid mathematical expression.")
        print(f"Calculation error: {e}")

def search_wikipedia(query):
    """Search Wikipedia for information"""
    try:
        wikipedia.set_user_agent("VoiceAssistant/1.0")
        results = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia")
        speak(results)
    except wikipedia.exceptions.DisambiguationError:
        speak("Multiple results found. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("Sorry, I couldn't find any information on that topic.")
    except Exception as e:
        speak("Sorry, I encountered an error while searching Wikipedia.")
        print(f"Wikipedia error: {e}")

def take_screenshot():
    """Take a screenshot and save it"""
    try:
        screenshot = pyautogui.screenshot()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        speak(f"Screenshot taken and saved as {filename}")
    except Exception as e:
        speak("Sorry, I couldn't take a screenshot")
        print(f"Screenshot error: {e}")

def open_system_app(app_name):
    """Open system applications in a cross-platform way"""
    try:
        if sys.platform.startswith('win'):
            if app_name == "notepad":
                os.system("start notepad.exe")
            elif app_name == "calculator":
                os.system("start calc.exe")
            elif app_name == "cmd":
                os.system("start cmd.exe")
        elif sys.platform.startswith('darwin'):
            if app_name == "notepad":
                subprocess.run(['open', '-a', 'TextEdit'])
            elif app_name == "calculator":
                subprocess.run(['open', '-a', 'Calculator'])
            elif app_name == "cmd":
                subprocess.run(['open', '-a', 'Terminal'])
        else:
            if app_name == "notepad":
                subprocess.run(['gedit'])
            elif app_name == "calculator":
                subprocess.run(['gnome-calculator'])
            elif app_name == "cmd":
                subprocess.run(['gnome-terminal'])
        
        speak(f"Opening {app_name}")
    except Exception as e:
        speak(f"Sorry, I couldn't open {app_name}")
        print(f"Error opening {app_name}: {e}")

def convert_units(value, from_unit, to_unit):
    """Convert between different units"""
    conversions = {
        "length": {
            "meter": 1, "meters": 1,
            "kilometer": 1000, "kilometers": 1000, "km": 1000,
            "centimeter": 0.01, "centimeters": 0.01, "cm": 0.01,
            "millimeter": 0.001, "millimeters": 0.001, "mm": 0.001,
            "inch": 0.0254, "inches": 0.0254, "in": 0.0254,
            "foot": 0.3048, "feet": 0.3048, "ft": 0.3048,
            "yard": 0.9144, "yards": 0.9144, "yd": 0.9144,
            "mile": 1609.34, "miles": 1609.34, "mi": 1609.34
        },
        "weight": {
            "gram": 1, "grams": 1, "g": 1,
            "kilogram": 1000, "kilograms": 1000, "kg": 1000,
            "milligram": 0.001, "milligrams": 0.001, "mg": 0.001,
            "pound": 453.592, "pounds": 453.592, "lb": 453.592, "lbs": 453.592,
            "ounce": 28.3495, "ounces": 28.3495, "oz": 28.3495
        },
        "temperature": {
            "celsius": lambda c: (c, (c * 9/5) + 32, c + 273.15),
            "fahrenheit": lambda f: ((f - 32) * 5/9, f, (f - 32) * 5/9 + 273.15),
            "kelvin": lambda k: (k - 273.15, (k - 273.15) * 9/5 + 32, k)
        }
    }
    
    # Normalize unit names (handle plurals and aliases)
    def normalize_unit(unit):
        unit_lower = unit.lower().strip()
        # Remove trailing 's' for plurals if exact match not found
        if unit_lower not in sum([list(units.keys()) for units in conversions.values()], []):
            if unit_lower.endswith('s'):
                unit_lower = unit_lower[:-1]
        return unit_lower
    
    from_unit_norm = normalize_unit(from_unit)
    to_unit_norm = normalize_unit(to_unit)
    
    # Try to find the conversion category
    category = None
    for cat, units in conversions.items():
        if from_unit_norm in units and to_unit_norm in units:
            category = cat
            break
    
    if category is None:
        speak("Sorry, I don't know how to convert between those units")
        return
    
    try:
        value = float(value)
        if category == "temperature":
            # Temperature conversion is different
            converted_values = conversions[category][from_unit_norm](value)
            if to_unit_norm == "celsius":
                result = converted_values[0]
            elif to_unit_norm == "fahrenheit":
                result = converted_values[1]
            else:  # kelvin
                result = converted_values[2]
        else:
            # Other conversions
            from_factor = conversions[category][from_unit_norm]
            to_factor = conversions[category][to_unit_norm]
            result = value * from_factor / to_factor
        
        speak(f"{value} {from_unit} is equal to {result:.2f} {to_unit}")
    except Exception as e:
        speak("Sorry, I couldn't perform that conversion")
        print(f"Conversion error: {e}")

# Smart Home Automation Functions
def connect_philips_hue():
    """Connect to Philips Hue bridge"""
    if not phue_available or not phue:
        speak("Philips Hue control is not available. Please install the phue module.")
        return None
        
    if not smart_home_config["philips_hue"]["enabled"]:
        speak("Philips Hue integration is not enabled in configuration.")
        return None
        
    try:
        bridge = phue.Bridge(smart_home_config["philips_hue"]["bridge_ip"])
        bridge.connect()
        smart_home_config["philips_hue"]["bridge"] = bridge
        speak("Connected to Philips Hue bridge")
        return bridge
    except Exception as e:
        speak("Failed to connect to Philips Hue bridge")
        print(f"Philips Hue connection error: {e}")
        return None

def control_light(light_name, action):
    """Control Philips Hue lights"""
    if not phue_available or not phue:
        speak("Philips Hue control is not available.")
        return
        
    bridge = smart_home_config["philips_hue"]["bridge"]
    if not bridge:
        bridge = connect_philips_hue()
        if not bridge:
            return
            
    try:
        light_id = smart_home_config["devices"].get(light_name, {}).get("id")
        if not light_id:
            speak(f"Light {light_name} not found in configuration")
            return
            
        if action == "on":
            bridge.set_light(light_id, 'on', True)
            speak(f"Turned {light_name} on")
        elif action == "off":
            bridge.set_light(light_id, 'on', False)
            speak(f"Turned {light_name} off")
        elif action.startswith("brightness"):
            try:
                brightness = int(action.split()[-1])
                # Ensure brightness is within valid range (0-255)
                brightness = max(0, min(255, brightness))
                bridge.set_light(light_id, 'bri', brightness)
                speak(f"Set {light_name} brightness to {brightness}")
            except ValueError:
                speak("Please specify a valid brightness level between 0 and 255")
        else:
            speak("Invalid action. Please use 'on', 'off', or 'brightness [level]'")
    except Exception as e:
        speak(f"Failed to control {light_name}")
        print(f"Light control error: {e}")

def control_smart_home(query):
    """Process smart home commands"""
    if "turn on" in query:
        # Extract device name
        for device_name in smart_home_config["devices"]:
            if device_name.replace("_", " ") in query:
                control_light(device_name, "on")
                return
        speak("I couldn't identify the device to turn on")
        
    elif "turn off" in query:
        # Extract device name
        for device_name in smart_home_config["devices"]:
            if device_name.replace("_", " ") in query:
                control_light(device_name, "off")
                return
        speak("I couldn't identify the device to turn off")
        
    elif "set brightness" in query:
        # Extract device name and brightness value
        for device_name in smart_home_config["devices"]:
            if device_name.replace("_", " ") in query:
                try:
                    brightness = int(re.findall(r'\d+', query)[0])
                    control_light(device_name, f"brightness {brightness}")
                    return
                except:
                    speak("Please specify a brightness level between 0 and 255")
                    return
        speak("I couldn't identify the device to adjust")

# File Management Functions
def search_files(keyword, path=None):
    """Search for files containing a keyword"""
    if path is None:
        path = os.path.expanduser("~")  # Search in home directory by default
    
    try:
        found_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if keyword.lower() in file.lower():
                    found_files.append(os.path.join(root, file))
                    if len(found_files) >= 10:  # Limit to 10 results
                        break
            if len(found_files) >= 10:
                break
        
        if found_files:
            speak(f"Found {len(found_files)} files containing '{keyword}'")
            for i, file_path in enumerate(found_files[:5]):  # Speak first 5 results
                speak(f"File {i+1}: {os.path.basename(file_path)}")
        else:
            speak(f"No files found containing '{keyword}'")
    except PermissionError:
        speak("Sorry, I don't have permission to search in that location")
    except Exception as e:
        speak("Sorry, I couldn't search for files")
        print(f"Search error: {e}")

def open_file(file_path):
    """Open a file with the default application"""
    try:
        # Expand user path if needed
        file_path = os.path.expanduser(file_path)
        
        if os.path.exists(file_path):
            if sys.platform.startswith('win'):
                os.startfile(file_path)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
            speak(f"Opening {os.path.basename(file_path)}")
        else:
            # Try to find the file in common directories
            common_paths = [
                file_management_config["downloads_path"],
                file_management_config["documents_path"],
                file_management_config["music_path"],
                file_management_config["pictures_path"]
            ]
            
            found = False
            for path in common_paths:
                full_path = os.path.join(path, file_path)
                if os.path.exists(full_path):
                    if sys.platform.startswith('win'):
                        os.startfile(full_path)
                    elif sys.platform.startswith('darwin'):
                        subprocess.run(['open', full_path])
                    else:
                        subprocess.run(['xdg-open', full_path])
                    speak(f"Opening {os.path.basename(full_path)}")
                    found = True
                    break
            
            if not found:
                speak("Sorry, I couldn't find that file")
    except Exception as e:
        speak("Sorry, I couldn't open that file")
        print(f"File opening error: {e}")

def list_directory_contents(path):
    """List contents of a directory"""
    try:
        if os.path.exists(path):
            items = os.listdir(path)
            speak(f"Found {len(items)} items in {path}")
            for i, item in enumerate(items[:10]):  # Speak first 10 items
                speak(f"Item {i+1}: {item}")
            if len(items) > 10:
                speak("And more items...")
        else:
            speak("Sorry, that directory doesn't exist")
    except PermissionError:
        speak("Sorry, I don't have permission to access that directory")
    except Exception as e:
        speak("Sorry, I couldn't list directory contents")
        print(f"Directory listing error: {e}")

# Advanced Web Browsing Functions
def search_web(query, search_engine="google"):
    """Search the web using different search engines"""
    try:
        # Properly encode the query for URL
        encoded_query = quote_plus(query)
        if search_engine == "google":
            url = f"https://www.google.com/search?q={encoded_query}"
        elif search_engine == "bing":
            url = f"https://www.bing.com/search?q={encoded_query}"
        elif search_engine == "duckduckgo":
            url = f"https://duckduckgo.com/?q={encoded_query}"
        else:
            url = f"https://www.google.com/search?q={encoded_query}"
        
        webbrowser.open(url)
        speak(f"Searching {search_engine} for {query}")
    except Exception as e:
        speak("Sorry, I couldn't perform the web search")
        print(f"Search error: {e}")

def open_website(website):
    """Open a specific website"""
    try:
        # Add http:// if not present
        if not website.startswith(("http://", "https://")):
            website = "https://" + website
        
        webbrowser.open(website)
        speak(f"Opening {website}")
    except Exception as e:
        speak("Sorry, I couldn't open that website")
        print(f"Website opening error: {e}")

def main():
    """Main function to run the voice assistant"""
    try:
        wishMe()
    except Exception as e:
        print(f"Error in wishMe: {e}")
        print("Assistant: Hello! How can I help you?")
    
    while True:
        try:
            query = takecommand().lower()
            if query == "none":
                continue
            
            # Debug output
            print(f"\n{'='*50}")
            print(f"Processing command: {query}")
            print(f"{'='*50}\n")
                
            check_reminders()  # Check for reminders
            check_scheduled_tasks()  # Check for scheduled tasks
            
            # Wikipedia search
            if 'wikipedia' in query or 'search wikipedia' in query:
                print(">>> Wikipedia command detected")
                try:
                    speak('Searching Wikipedia...')
                    # Remove both "wikipedia" and "search" keywords
                    search_query = query.replace("wikipedia", "").replace("search", "").strip()
                    print(f">>> Wikipedia search query: '{search_query}'")
                    if search_query:
                        search_wikipedia(search_query)
                        print(">>> Wikipedia search completed")
                    else:
                        speak("What would you like to search on Wikipedia?")
                except Exception as e:
                    print(f">>> Wikipedia command error: {e}")
                    import traceback
                    traceback.print_exc()
                    speak("Sorry, I couldn't search Wikipedia")

            # Web browsing
            elif 'open youtube' in query:
                try:
                    webbrowser.open("youtube.com")
                    speak("Opening YouTube")
                except Exception as e:
                    speak("Sorry, I couldn't open YouTube")
                    print(f"Error opening YouTube: {e}")

            elif 'open google' in query:
                try:
                    webbrowser.open("google.com")
                    speak("Opening Google")
                except Exception as e:
                    speak("Sorry, I couldn't open Google")
                    print(f"Error opening Google: {e}")

            elif 'play music' in query:
                try:
                    webbrowser.open("https://music.youtube.com")
                    speak("Opening YouTube Music")
                except Exception as e:
                    speak("Sorry, I couldn't open music")
                    print(f"Error opening music: {e}")

            # Time
            elif 'the time' in query or 'what time' in query or 'current time' in query or 'time now' in query:
                print(">>> Time command detected")
                try:
                    strTime = datetime.datetime.now().strftime("%H:%M:%S")
                    speak(f"The current time is {strTime}")
                    print(f">>> Time response sent: {strTime}")
                except Exception as e:
                    print(f">>> Time command error: {e}")
                    speak("Sorry, I couldn't get the time")

            # System applications
            elif 'open notepad' in query:
                open_system_app("notepad")

            elif 'open calculator' in query:
                open_system_app("calculator")

            elif 'open command prompt' in query:
                open_system_app("cmd")

            # Weather and news
            elif 'weather in' in query or 'weather for' in query or ('weather' in query and len(query.split()) > 2):
                print(">>> Weather command detected")
                try:
                    # Extract city name
                    if 'weather in' in query:
                        city = query.replace('weather in', '').strip()
                    elif 'weather for' in query:
                        city = query.replace('weather for', '').strip()
                    else:
                        # Just "weather" - try to extract city after weather
                        parts = query.split('weather')
                        if len(parts) > 1:
                            city = parts[1].strip()
                        else:
                            city = ""
                    
                    print(f">>> Weather city extracted: {city}")
                    if city:
                        get_weather(city)
                    else:
                        speak("Which city's weather would you like to know?")
                except Exception as e:
                    print(f">>> Weather command error: {e}")
                    import traceback
                    traceback.print_exc()
                    speak("Sorry, I couldn't get the weather")

            elif 'tell me the news' in query or "what's in the news" in query or 'news' in query:
                get_news()

            # Reminders
            elif 'set reminder for' in query:
                try:
                    # Extract time and reminder text
                    parts = query.split('set reminder for')
                    if len(parts) > 1:
                        time_text = parts[1].strip()
                        # Simple time parsing (you can enhance this)
                        if 'minute' in time_text:
                            minutes = int(re.findall(r'\d+', time_text)[0])
                            set_reminder("Your reminder", minutes * 60)
                        elif 'second' in time_text:
                            seconds = int(re.findall(r'\d+', time_text)[0])
                            set_reminder("Your reminder", seconds)
                        else:
                            speak("Please specify time in minutes or seconds")
                    else:
                        speak("What would you like me to remind you about?")
                        reminder_text = takecommand()
                        if reminder_text != "none":
                            speak("In how many seconds should I remind you?")
                            time_text = takecommand()
                            if time_text != "none":
                                seconds = int(re.findall(r'\d+', time_text)[0])
                                set_reminder(reminder_text, seconds)
                except Exception as e:
                    speak("Sorry, I couldn't set the reminder. Please try again.")
                    print(f"Reminder error: {e}")

            # Scheduled tasks
            elif 'schedule task' in query:
                try:
                    # Extract task description and time
                    parts = query.split('schedule task')
                    if len(parts) > 1:
                        task_text = parts[1].strip()
                        speak("When should I schedule this task?")
                        time_text = takecommand()
                        if time_text != "none":
                            # Parse time (this is a simple implementation)
                            schedule_time = datetime.datetime.now() + datetime.timedelta(minutes=5)  # Default 5 minutes
                            schedule_task(task_text, schedule_time)
                    else:
                        speak("What task would you like me to schedule?")
                        task_text = takecommand()
                        if task_text != "none":
                            speak("When should I schedule this task?")
                            time_text = takecommand()
                            if time_text != "none":
                                schedule_time = datetime.datetime.now() + datetime.timedelta(minutes=5)  # Default 5 minutes
                                schedule_task(task_text, schedule_time)
                except Exception as e:
                    speak("Sorry, I couldn't schedule the task. Please try again.")
                    print(f"Scheduling error: {e}")

            # System information
            elif 'system info' in query or 'system status' in query or 'system information' in query:
                print(">>> System info command detected")
                try:
                    get_system_info()
                except Exception as e:
                    print(f">>> System info error: {e}")
                    speak("Sorry, I couldn't get system information")

            # Entertainment
            elif 'tell me a joke' in query or 'joke' in query or 'tell a joke' in query:
                print(">>> Joke command detected")
                try:
                    tell_joke()
                except Exception as e:
                    print(f">>> Joke error: {e}")
                    speak("Sorry, I couldn't tell a joke")

            elif 'tell me a quote' in query or 'inspire me' in query or 'quote' in query or 'inspirational quote' in query:
                print(">>> Quote command detected")
                try:
                    tell_quote()
                except Exception as e:
                    print(f">>> Quote error: {e}")
                    speak("Sorry, I couldn't get a quote")

            # Calculations
            elif 'calculate' in query:
                print(">>> Calculate command detected")
                try:
                    expression = query.replace('calculate', '').strip()
                    # Remove common question words
                    expression = re.sub(r'^(the|a|an)\s+', '', expression, flags=re.IGNORECASE)
                    expression = expression.strip()
                    
                    print(f">>> Calculation expression: '{expression}'")
                    if expression:
                        calculate(expression)
                        print(">>> Calculation completed")
                    else:
                        speak("What would you like me to calculate?")
                except Exception as e:
                    speak("Sorry, I couldn't calculate that")
                    print(f">>> Calculation error: {e}")
                    import traceback
                    traceback.print_exc()

            # Unit conversion
            elif 'convert' in query:
                try:
                    print(">>> Convert command detected")
                    # Simple conversion parsing
                    parts = query.split('convert')
                    if len(parts) > 1:
                        conversion_text = parts[1].strip()
                        # Example: "convert 10 meters to feet"
                        words = conversion_text.split()
                        if len(words) >= 4 and words[2].lower() == "to":
                            value = words[0]
                            from_unit = words[1]
                            to_unit = words[3]
                            print(f">>> Converting: {value} {from_unit} to {to_unit}")
                            convert_units(value, from_unit, to_unit)
                        elif len(words) >= 3:
                            # Try to handle without "to" - e.g., "convert 32 fahrenheit celsius"
                            value = words[0]
                            from_unit = words[1]
                            to_unit = words[2]
                            print(f">>> Converting: {value} {from_unit} to {to_unit}")
                            convert_units(value, from_unit, to_unit)
                        else:
                            speak("Please specify conversion in format: convert value from_unit to to_unit")
                    else:
                        speak("What would you like me to convert?")
                except Exception as e:
                    speak("Sorry, I couldn't perform that conversion")
                    print(f">>> Conversion error: {e}")
                    import traceback
                    traceback.print_exc()

            # Screenshot
            elif 'take screenshot' in query or 'screenshot' in query:
                print(">>> Screenshot command detected")
                try:
                    take_screenshot()
                except Exception as e:
                    print(f">>> Screenshot error: {e}")
                    speak("Sorry, I couldn't take a screenshot")

            # Smart Home Automation
            elif 'turn on' in query or 'turn off' in query or 'set brightness' in query or 'brightness' in query:
                print(">>> Smart home command detected")
                try:
                    control_smart_home(query)
                except Exception as e:
                    print(f">>> Smart home error: {e}")
                    speak("Sorry, I couldn't control the smart home device")

            # File Management
            elif 'search files for' in query or 'search for files' in query or 'find files' in query:
                print(">>> File search command detected")
                try:
                    if 'search files for' in query:
                        keyword = query.replace('search files for', '').strip()
                    elif 'search for files' in query:
                        keyword = query.replace('search for files', '').strip()
                    else:
                        keyword = query.replace('find files', '').strip()
                    if keyword:
                        print(f">>> Searching for files: {keyword}")
                        search_files(keyword)
                    else:
                        speak("What would you like to search for in files?")
                except Exception as e:
                    print(f">>> File search error: {e}")
                    speak("Sorry, I couldn't search for files")

            elif 'open file' in query:
                print(">>> Open file command detected")
                try:
                    file_path = query.replace('open file', '').strip()
                    if file_path:
                        print(f">>> Opening file: {file_path}")
                        open_file(file_path)
                    else:
                        speak("Which file would you like to open?")
                except Exception as e:
                    print(f">>> Open file error: {e}")
                    speak("Sorry, I couldn't open that file")

            elif 'list directory' in query or 'list folder' in query or 'show directory' in query:
                print(">>> List directory command detected")
                try:
                    if 'list directory' in query:
                        path = query.replace('list directory', '').strip()
                    elif 'list folder' in query:
                        path = query.replace('list folder', '').strip()
                    else:
                        path = query.replace('show directory', '').strip()
                    if not path:
                        path = os.getcwd()  # Current directory
                    print(f">>> Listing directory: {path}")
                    list_directory_contents(path)
                except Exception as e:
                    print(f">>> List directory error: {e}")
                    speak("Sorry, I couldn't list the directory")

            # Advanced Web Browsing
            elif 'search web for' in query or 'search the web' in query or 'google search' in query:
                print(">>> Web search command detected")
                try:
                    if 'search web for' in query:
                        search_query = query.replace('search web for', '').strip()
                    elif 'search the web' in query:
                        search_query = query.replace('search the web', '').strip()
                    else:
                        search_query = query.replace('google search', '').strip()
                    if search_query:
                        print(f">>> Web search query: {search_query}")
                        search_web(search_query)
                    else:
                        speak("What would you like to search for on the web?")
                except Exception as e:
                    print(f">>> Web search error: {e}")
                    speak("Sorry, I couldn't perform the web search")

            elif 'open website' in query or 'open' in query:
                print(">>> Open website command detected")
                try:
                    if 'open website' in query:
                        website = query.replace('open website', '').strip()
                    elif 'open' in query and 'open notepad' not in query and 'open calculator' not in query and 'open command prompt' not in query:
                        # Extract website from "open [website]"
                        parts = query.split('open', 1)
                        if len(parts) > 1:
                            website = parts[1].strip()
                        else:
                            website = ""
                    if website:
                        print(f">>> Opening website: {website}")
                        open_website(website)
                    else:
                        speak("Which website would you like to open?")
                except Exception as e:
                    print(f">>> Open website error: {e}")
                    speak("Sorry, I couldn't open that website")

            # System commands
            elif 'shutdown' in query:
                speak("Are you sure you want to shutdown the system?")
                confirmation = takecommand().lower()
                if 'yes' in confirmation:
                    try:
                        if sys.platform.startswith('win'):
                            os.system("shutdown /s /t 1")
                        else:
                            os.system("shutdown -h now")
                    except Exception as e:
                        speak("Sorry, I couldn't shutdown the system")
                        print(f"Shutdown error: {e}")
                else:
                    speak("Shutdown cancelled")

            elif 'restart' in query:
                speak("Are you sure you want to restart the system?")
                confirmation = takecommand().lower()
                if 'yes' in confirmation:
                    try:
                        if sys.platform.startswith('win'):
                            os.system("shutdown /r /t 1")
                        else:
                            os.system("reboot")
                    except Exception as e:
                        speak("Sorry, I couldn't restart the system")
                        print(f"Restart error: {e}")
                else:
                    speak("Restart cancelled")

            # Exit commands
            elif 'exit' in query or 'quit' in query or 'goodbye' in query:
                speak("Goodbye! Have a great day!")
                sys.exit()
            
            # Fallback for unrecognized commands
            else:
                speak("I didn't understand that command. Please try again or say 'exit' to quit.")
                print(f"Unrecognized command: {query}")
                
            time.sleep(0.1)
        except KeyboardInterrupt:
            speak("Goodbye! Have a great day!")
            print("\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"\n!!! ERROR IN MAIN LOOP: {e} !!!")
            import traceback
            traceback.print_exc()
            speak("Sorry, an error occurred. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()