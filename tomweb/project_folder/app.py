from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
from transformers import pipeline
from datetime import datetime
from flask import Flask, render_template
import Flask, render_template
import random
import time
import webbrowser
import wikipedia
from googlesearch import search
import cv2
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)



# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Load a local NLP model (distilbert-base-uncased-finetuned-sst-2-english for sentiment-analysis)
nlp = pipeline("sentiment-analysis")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    command = data['command']
    response, _ = respond(command, "User")
    return jsonify({'response': response})

def take_photo():
    save_path = r"D:\login error"
    file_name = "captured_image.png"
    
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    full_path = os.path.join(save_path, file_name)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return "Error: Could not open video device."
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    ret, frame = cap.read()
    
    if ret:
        cv2.imwrite(full_path, frame)
        send_email(to_address="sivasiva60022@gmail.com", subject="AI", body="Someone is trying to login", attachment_path=full_path)
        cap.release()
        return f"Photo captured and saved as {full_path}"
    else:
        return "Error: Could not read frame."

    cap.release()

def send_email(to_address, subject, body, attachment_path):
    from_address = "tom872024@gmail.com"
    app_password = "fpra cspa zcai aadv" 

    try:
        validate_email(to_address)
        
        message = MIMEMultipart()
        message['From'] = from_address
        message['To'] = to_address
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {attachment_path}",
                )
                message.attach(part)

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(from_address, app_password)
        text = message.as_string()
        session.sendmail(from_address, to_address, text)
        session.quit()

        return 'Mail Sent'

    except EmailNotValidError as e:
        return str(e)
    except Exception as e:
        return f"An error occurred: {e}"

def respond(text, user_name):
    if "weather" in text.lower():
        response_text = get_weather()
    elif "joke" in text.lower():
        response_text = tell_joke()
    elif "time" in text.lower():
        response_text = get_time()
    elif "news" in text.lower():
        response_text = get_news()
    elif "quote" in text.lower():
        response_text = get_quote()
    elif "calculate" in text.lower():
        expression = text.lower().replace("calculate", "").strip()
        response_text = calculate(expression)
    elif "open" in text.lower():
        url = text.lower().replace("open", "").strip()
        if not url.startswith("http"):
            url = "http://" + url + ".com"
        response_text = open_website(url)
    elif "search" in text.lower():
        query = text.lower().replace("search", "").strip()
        response_text = search_web(query)
    elif 'wikipedia' in text.lower():
        query = text.lower().replace("wikipedia", "").strip()
        response_text = f"Searching Wikipedia for {query}"
        results = wikipedia.summary(query, sentences=2)
        response_text += f"\nAccording to Wikipedia: {results}"
    else:
        result = nlp(text)
        response_text = f"The sentiment is: {result[0]['label']} with a score of {result[0]['score']:.2f}"
    
    return response_text, user_name

def get_weather():
    return "The weather is sunny with a high of 25 degrees Celsius."

def tell_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don't skeletons fight each other? They don't have the guts."
    ]
    return random.choice(jokes)

def get_time():
    now = datetime.now()
    return f"The current time is {now.strftime('%H:%M:%S')}"

def get_news():
    headlines = [
        "The stock market hits an all-time high.",
        "New species of dinosaur discovered in Argentina.",
        "Tech company announces breakthrough in AI research."
    ]
    return "Here are today's headlines: " + ", ".join(headlines)

def get_quote():
    quotes = [
        "The best way to get started is to quit talking and begin doing. - Walt Disney",
        "The pessimist sees difficulty in every opportunity. The optimist sees opportunity in every difficulty. - Winston Churchill",
        "Don’t let yesterday take up too much of today. - Will Rogers"
    ]
    return random.choice(quotes)

def calculate(expression):
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}."
    except Exception as e:
        return f"Sorry, I couldn't calculate that. {e}"

def open_website(url):
    try:
        webbrowser.open(url)
        return f"Opening {url}"
    except Exception as e:
        return f"Sorry, I couldn't open {url}. {e}"

def search_web(query):
    try:
        search_results = list(search(query, num_results=3)) 
        if search_results:
            return f"Top results for {query} are: {', '.join(search_results)}"
        else:
            return f"No results found for {query}."
    except Exception as e:
        return f"Sorry, I couldn't search for {query}. {e}"

if __name__ == '__main__':
    app.run(debug=True)
