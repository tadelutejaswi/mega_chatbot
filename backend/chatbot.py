import openai
import random
import requests
import csv
import os

from data_processing import DataProcessor

class MegaChatbot:
    def __init__(self, knowledge_file):
        self.data_processor = DataProcessor(knowledge_file)
        self.context = {}
        # Initialize API keys from environment variables
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.weather_key = os.getenv("WEATHER_API_KEY")
        openai.api_key = self.openai_key

    def respond(self, user_input, user_id='default'):
        try:
            # 1. Check for weather queries first
            if any(word in user_input.lower() for word in ['weather', 'forecast', 'temperature']):
                city = self._extract_city(user_input)
                weather = self._get_weather(city)
                if weather: return weather

            # 2. Check knowledge base
            kb_response = self._check_knowledge_base(user_input)
            if kb_response: return kb_response

            # 3. Fallback to OpenAI
            ai_response = self._get_ai_response(user_input)
            if ai_response: return ai_response

            # 4. Final fallback
            return self._get_fallback_response()
            
        except Exception as e:
            print(f"Error in respond(): {e}")
            return "Sorry, I encountered an error. Please try again."

    def _extract_city(self, text):
        text = text.lower()
        for phrase in ['weather in', 'forecast for', 'temperature in']:
            if phrase in text:
                return text.split(phrase)[1].split('?')[0].strip()
        return "London"  # default city

    def _get_weather(self, city):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_key}"
            response = requests.get(url).json()
            if response.get('cod') == 200:
                temp = round(response['main']['temp'] - 273.15, 1)  # Kelvin to Celsius
                desc = response['weather'][0]['description']
                return f"Weather in {city}: {temp}°C, {desc}"
            return f"Couldn't get weather for {city}"
        except:
            return "Weather service unavailable"

    def _check_knowledge_base(self, user_input):
        kb = self.data_processor.get_knowledge_base()
        user_input = user_input.lower().strip(' ?.!')
        
        for entry in kb:
            if 'question' in entry and 'answer' in entry:
                q = entry['question'].lower().strip(' ?.!')
                if q in user_input or user_input in q:
                    return entry['answer']
        return None

    def _get_ai_response(self, user_input):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_input}],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except:
            return None

    def _get_fallback_response(self):
        fallbacks = [
            "I'm not sure I understand. Could you rephrase?",
            "That's an interesting question. Let me think...",
            "I don't have an answer for that right now.",
            "Could you ask that differently?"
        ]
        return random.choice(fallbacks)

    def get_random_question(self):
        kb = self.data_processor.get_knowledge_base()
        questions = [q['question'] for q in kb if 'question' in q]
        return random.choice(questions) if questions else "Ask me anything"
