import openai
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chatbot import MegaChatbot
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")

# Initialize chatbot with correct path
chatbot = MegaChatbot('knowledge_base.csv')

@app.route('/')
def home():
    """Root route with a simple welcome message"""
    return "Welcome to the Mega Chatbot API!"

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon"""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Handle chat messages with proper error handling"""
    try:
        data = request.get_json()
        if not data or 'message' not in data or not data['message'].strip():
            return jsonify({'error': 'Message is required'}), 400
            
        response = chatbot.respond(data['message'].strip())
        return jsonify({'response': response})
        
    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/random-question', methods=['GET'])
def random_question():
    """Get a random question from knowledge base"""
    try:
        question = chatbot.get_random_question()
        return jsonify({'question': question})
    except Exception as e:
        app.logger.error(f"Random question error: {str(e)}")
        return jsonify({'error': 'Failed to get random question'}), 500

@app.route('/weather', methods=['GET'])
def weather():
    """Get weather data with robust error handling"""
    try:
        city = request.args.get('city', 'London').strip()
        if not city:
            return jsonify({'error': 'City parameter is required'}), 400
            
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}"
        response = requests.get(url, timeout=5).json()
        
        if response.get("cod") != 200:
            return jsonify({'error': response.get('message', 'City not found')}), 404
        
        weather_data = {
            'city': city,
            'temperature': round(response['main']['temp'] - 273.15, 1),  # Convert to Celsius
            'description': response['weather'][0]['description'],
            'humidity': response['main']['humidity'],
            'wind_speed': response['wind']['speed']
        }
        return jsonify(weather_data)
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Weather service timeout'}), 504
    except Exception as e:
        app.logger.error(f"Weather error: {str(e)}")
        return jsonify({'error': 'Failed to fetch weather data'}), 500

@app.route('/ask-openai', methods=['POST'])
def ask_openai():
    """Direct OpenAI query endpoint with validation"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated to current recommended model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return jsonify({'response': response.choices[0].message.content.strip()})
        
    except openai.error.OpenAIError as e:
        app.logger.error(f"OpenAI error: {str(e)}")
        return jsonify({'error': 'OpenAI service error'}), 502
    except Exception as e:
        app.logger.error(f"OpenAI endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')  # Accessible on all network interfaces
