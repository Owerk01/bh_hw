import flask
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# GROQ_API_KEY=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
# WEATHER_API_KEY=2a4ff86f9aaa70041ec8e82db64abf56

BASE_DIR = os.path.dirname(__file__)

app = flask.Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, "templates"),
            static_folder=os.path.join(BASE_DIR, "static"))

@app.route('/')
def index():
    return '<h1>Main Page</h1>'

@app.route("/duck/")
def ducks():
    res = requests.get("https://random-d.uk/api/random")
    res = res.json()
    url = res["url"]
    num = url.split('/')[-1].split('.')[0]
    return f'<h1>Random Duck №{num}</h1>\n<img src="{url}" alt="no image">'

@app.route("/foxes/<int:counter>/")
def foxes(counter):
    if counter > 10:
        return "Number of foxes must be less than 10"
    answer = ""
    for _ in range(counter):
        res = requests.get("https://randomfox.ca/floof")
        res = res.json()
        image = res["image"]
        num = image.split('/')[-1].split('.')[0]
        answer += f'<h1>Random Fox №{num}</h1>\n<img src="{image}" alt="no image">\n'
    return answer

@app.route("/weather-minsk/")
def weather_minsk():
    params = {'q': "Minsk", 'APPID': f'{WEATHER_API_KEY}'}
    res = requests.get("http://api.openweathermap.org/data/2.5/weather", params)
    res = res.json()

    return f'Minsk: {res["weather"][0]["main"]}'

@app.route("/weather/<city>/")
def weather_city(city):
    params = {'q': f"{city}", 'APPID': f'{WEATHER_API_KEY}'}
    res = requests.get("http://api.openweathermap.org/data/2.5/weather", params)
    res = res.json()

    return f'{city}: {res["weather"][0]["main"]}'

@app.route("/llm/<question>/")
def llm(question: str):
    headers = {"Content-Type": "application/json", 
               "Authorization": f"{GROQ_API_KEY}"}
    data = {"model": "llama-3.3-70b-versatile",
            "messages": [{
                "role": "user",
                "content": f"{question.replace('_', ' ')}"
            }]
            }
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
    res = res.json()

    return f'answer: {res["choices"][0]["message"]["content"]}'

@app.errorhandler(404)
def page_not_found(error):
    return '<h1 style="color:red"> такой страницы не существует </h1>'

app.run(debug=True)