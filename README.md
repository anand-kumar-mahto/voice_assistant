Voice Assistant

A Python based voice controlled AI assistant that performs real time tasks using speech recognition and text to speech. It enables web access, system control, file management, automation, and productivity features through natural voice commands.
-------------------------------------------------------------------------------------------------------------
Features
1. Voice Interaction

Speech recognition using Google Speech Recognition API

Text to speech using pyttsx3 with SAPI5 support on Windows

Time based greeting system

Continuous listening until exit command

2. Web and Information Access

Wikipedia search with summarized responses

Web search using Google, Bing, or DuckDuckGo

Open websites such as YouTube and Google

YouTube Music access

3. Weather and News

Current weather by city using OpenWeatherMap API

Displays temperature, feels like value, humidity, and description

Top five news headlines using NewsAPI

4. Time and Task Management

Current time retrieval

Set reminders in seconds or minutes

Schedule tasks by description

5. Calculations and Conversions

Arithmetic operations including addition, subtraction, multiplication, division, and powers

Unit conversions

Length
meters, kilometers, centimeters, millimeters, inches, feet, yards, miles

Weight
grams, kilograms, milligrams, pounds, ounces

Temperature
Celsius, Fahrenheit, Kelvin

6. System Control

CPU, memory, and battery monitoring using psutil

Launch applications such as Notepad, Calculator, Terminal, Command Prompt

Capture screenshots with timestamp file naming

Shutdown and restart with voice confirmation

7. File Management

Search files by keyword within home directory

Open files from Downloads, Documents, Music, and Pictures

List directory contents with limited output

8. Smart Home Integration Optional

Philips Hue light control using phue

Turn lights on or off

Adjust brightness from 0 to 255

9. Entertainment

Random jokes

Inspirational quotes
-------------------------------------------------------------------------------------------------------------

Installation
Requirements

Python 3.6 or higher

Microphone

Internet connection for recognition and web features

Install Dependencies

pip install pyttsx3
pip install SpeechRecognition
pip install pyautogui
pip install wikipedia
pip install requests
pip install psutil

Optional

pip install phue

Platform Setup

Windows

SAPI5 supported by default

Linux

Install portaudio19 dev

Install python3 pyaudio

macOS

Install portaudio using Homebrew

pip install pyaudio
-------------------------------------------------------------------------------------------------------------

API Configuration

Set environment variables

Windows PowerShell
set WEATHER_API_KEY
set NEWS_API_KEY

Linux or macOS
export WEATHER_API_KEY
export NEWS_API_KEY

Optional config.py allows

Assistant name customization

Smart home configuration

Custom file paths
-------------------------------------------------------------------------------------------------------------

Usage

Run
python voice_assistant_improved.py

Workflow

Start the script

Speak when listening prompt appears

Wait for response

Say exit or quit to terminate
-------------------------------------------------------------------------------------------------------------

Troubleshooting

Speech recognition issues

Check microphone permissions

Ensure stable internet connection

Reduce background noise

Text to speech issues

Verify pyttsx3 installation

Confirm system voice engine availability

Module errors

Install missing dependencies

API issues

Verify API keys

Check rate limits
-------------------------------------------------------------------------------------------------------------

Security and Privacy

Voice input processed via Google Speech Recognition

API keys should be stored securely

Shutdown and restart require confirmation

File operations execute only on explicit command
