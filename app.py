import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import os
import google.generativeai as genai
import random
import chardet
import fitz
import secrets

print(secrets.token_hex(32))

load_dotenv()  # Load .env variables

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


# Setup Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
qa_history = []

last_joke = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip().lower()

    current_hour = datetime.now().hour
    if current_hour < 12:
        time_greet = "Good morning"
    elif current_hour < 18:
        time_greet = "Good afternoon"
    else:
        time_greet = "Good evening"

    # 🌟 Greetings
    if any(kw in question for kw in ["hi griv", "hello griv", "hey griv", "hai griv","is your name griv"]):
        return jsonify({"answer": f" glad you know my name! 😊"})

    if question in ["hi", "hello", "hey", "hai", "hii", "helo", "heyy","hiii"]:
        return jsonify({"answer": f"{time_greet}! GRIV here, how can I assist you today? 😊"})

    #cool greeting
    if question in ["hey bro","yo bro","hi bro","hello bro"]:
        return jsonify({"answer": f" what's up dude 😎, how can i help you?"})

    # 🔤 Name-related
    if any(x in question for x in [
        "your name", "who are you", "what are you", "what's your name",
        "what is your name", "what is ur name", "wht is ur name", "wht ur name",
        "name", "Name", "What is ur name", "Wht is ur name", "NAME",
        "wat is ur name", "Wat is your name"
    ]):
        return jsonify({"answer": "Hello, I'm GRIV — your AI chatbot assistant! 🤖"})

    # 😄 Friendly response to appreciation
    if any(kw in question for kw in ["thank you", "thanks", "thankyou", "thanks griv", "thank you very much"]):
        return jsonify({"answer": "You're welcome! Always here to help 😊"})

    # 😎 Friendly acknowledgment of understanding
    if any(kw in question for kw in ["oh i got it", "i understood", "now i understood", "got it", "okay got it"]):
        return jsonify({"answer": "Glad it makes sense now! Let me know if anything else is confusing 🤝"})

    # 🤝 Human-like reply to "how are you"
    if "how are you" in question or "how r u" in question or "how r u?" in question:
        return jsonify({"answer": "I'm doing great! Thanks for asking 😊 How can I help you today?"})

    if "thank you" in question or "thanks" in question or "thankyou" in question or "thank you griv" in question:
        return jsonify({'answer': "You're welcome! 😊 Always here to help."})

    if "how are you" in question or "how's it going" in question or "are you okay" in question or "how do you feel" in question:
        return jsonify({'answer': "I'm doing great! Thanks for asking 🤖 How can I help you today?"})

    if "i understood" in question or "now i got it" in question or "okay got it" in question or "oh okay" in question or "that makes sense" in question:
        return jsonify({'answer': "Awesome! Glad it’s clear now 🙌"})

    if "you're the best" in question or "griv you're awesome" in question or "good job" in question or "great answer" in question:
        return jsonify({'answer': "You're too kind! Thanks a lot 😄"})

    if "i love you" in question or "love you griv" in question:
        return jsonify({'answer': "Aww, I love helping you too! ❤️"})

    if "who created you" in question or  "who created u" in question or "who made you" in question or "who made u" in question or "who is your developer" in question or "who created u" in question or "who built you" in question or "who built u" in question :
        return jsonify({'answer': "I was built with passion and code by my awesome creator Ibrahim ! 🛠️"})

    if "are you real" in question or "are you alive" in question or "do you have feelings" in question:
        return jsonify({'answer': "Not quite alive, but I’m here for real-time conversations! 😄"})

    if "good morning" in question or "good afternoon" in question or "good evening" in question:
        return jsonify({'answer': "Wishing you a pleasant day! 😊 What can I help you with?"})

    if "what is my name" in question or "What is my name?" in question or "whts my name" in question or "my name" in question :
        return jsonify({"answer": "sorry ,i don't know your name. please tell me"})


    #joke handler
    # 🃏 Smart Joke Handler (avoids repeating last joke)
    if "joke" in question or "make me laugh" in question or "say something funny" in question:
        jokes = [
            "Why don’t programmers like nature? It has too many bugs! 🐛",
            "Why did the developer go broke? Because he used up all his cache! 💸",
            "Why do Java developers wear glasses? Because they don’t see sharp. 🤓",
            "What’s a programmer’s favorite hangout place? The Foo Bar! 🍸",
            "Why did the computer get cold? It forgot to close its Windows! 🪟❄️"
        ]

        # Select a joke that's different from the last one
        global last_joke
        available_jokes = [j for j in jokes if j != last_joke]
        if not available_jokes:
            available_jokes = jokes  # Reset if all jokes used

        selected_joke = random.choice(available_jokes)
        last_joke = selected_joke  # Update tracker

        return jsonify({'answer': selected_joke})

    if "ok" in question or "okay" in question or "fine" in question or "cool" in question:
        return jsonify({'answer': "Great! Let me know if you need anything else ✨"})

    if "bye" in question or "goodbye" in question or "see you" in question or "see you later" in question:
        return jsonify({'answer': "Take care! Catch you soon 👋"})

    if "tell me a joke" in question or "make me laugh" in question or "say something funny" in question:
        return jsonify({'answer': "Why don’t programmers like nature? It has too many bugs! 🐛"})

    if "sing a song" in question or "can you sing" in question or "give me lyrics" in question:
        return jsonify({'answer': "🎵 I'm not a singer, but I can surely find you some cool lyrics!"})

    if "do you sleep" in question or "when do you sleep" in question or "need rest?" in question:
        return jsonify({'answer': "No sleep for me! I’m always awake for you 😴❌"})

    if "griv" in question or "griv?" in question or "hey griv" in question:
        return jsonify({'answer': "Yes? I'm here and ready to help! 😊"})

    if "what can you do" in question or "help" in question or "what are your skills" in question or "what can u do"in question:
        return jsonify({'answer': "I can answer questions, explain code, summarize files, and more. Just ask! 💡"})

        # ⏰ Greeting logic, name, jokes, thank yous... (keep your existing blocks here)

    # 🕒 Time
    if "time" in question:
        now = datetime.now().strftime("%I:%M %p")
        return jsonify({"answer": f"The current time is {now}."})

    # 📅 Date
    if "date" in question:
        today = datetime.now().strftime("%A, %d %B %Y")
        return jsonify({"answer": f"Today's date is {today}."})

    # 🌦️ Weather
    if "weather" in question:
        weather_api = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": "Chennai",
            "appid": "YOUR_OPENWEATHERMAP_API_KEY",  # Replace with your API key
            "units": "metric"
        }
        try:
            res = requests.get(weather_api, params=params)
            weather_data = res.json()
            temp = weather_data['main']['temp']
            desc = weather_data['weather'][0]['description']
            return jsonify({"answer": f"🌦️ It's currently {temp}°C with {desc} in Chennai."})
        except:
            return jsonify({"answer": "⚠️ Unable to fetch weather info."})

    # 💬 Default Gemini fallback reply
    else:
        try:
            history = "\n".join([f"User: {q}\nGRIV: {a}" for q, a in qa_history[-5:]])  # limit to last 5

            # Detect if user wants table or comparison
            if "table difference" in question or "difference between" in question or "diff btwn" in question:
                prompt = (
                    f"You are GRIV, a helpful AI assistant.\n"
                    f"Please provide the differences in a well-formatted markdown table using | separators.\n\n"
                    f"{question}"
                )
            elif "compare and contrast" in question:
                prompt = (
                    f"You are GRIV, a helpful AI assistant.\n"
                    f"Provide a compare-and-contrast answer in clear bullet points. Use '•' or '-' for each point.\n\n"
                    f"{question}"
                )
            else:
                prompt = (
                    f"You are GRIV, a friendly and smart assistant. "
                    f"Give clear and concise answers without asking the user to rephrase. "
                    f"If the prompt is vague, make a best guess.\n\n"
                    f"Even if the question is short or unclear, try to give a working code or example based on common use cases.\n\n"
                    f"{history}\nUser: {question}\nGRIV:"
                )

            response = model.generate_content(prompt)

            answer = response.text.strip().removeprefix("GRIV:").strip()

            qa_history.append((question, answer))
            return jsonify({"answer": answer})
        except Exception as e:
            return jsonify({"answer": f"⚠️ Error: {str(e)}"})


@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files['file']
    instruction = request.form.get("instruction", "").lower()

    try:
        filename = uploaded_file.filename.lower()
        raw_bytes = uploaded_file.read()

        if filename.endswith(".pdf"):
            with fitz.open(stream=raw_bytes, filetype="pdf") as doc:
                content = ""
                for page in doc:
                    content += page.get_text()
        else:
            detected = chardet.detect(raw_bytes)
            encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            content = raw_bytes.decode(encoding, errors='replace')

        content = content[:3000]  # Limit to 3k chars

        # Dynamic prompt based on instruction
        if "summarize" in instruction:
            prompt = f"Give a short 7 to 15 line summary of the following content:\n\n{content}"
        elif "author" in instruction:
            prompt = f"Identify the author or creator of the following content:\n\n{content}"
        elif "lessons" in instruction:
            prompt = f"What are the lessons or key takeaways from the following content?\n\n{content}"
        elif "questions" in instruction:
            prompt = f"Frame 5 important questions based on the following content:\n\n{content}"
        else:
            prompt = f"Read and explain this content:\n\n{content}"

        response = model.generate_content(prompt)
        summary = response.text.strip()

        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"summary": f"⚠️ Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
