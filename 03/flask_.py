import flask
import os
import requests

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
    params = {'q': "Minsk", 'APPID': '2a4ff86f9aaa70041ec8e82db64abf56'}
    res = requests.get("http://api.openweathermap.org/data/2.5/weather", params)
    res = res.json()

    return f'Minsk: {res["weather"][0]["main"]}'

@app.route("/weather/<city>/")
def weather_city(city):
    params = {'q': f"{city}", 'APPID': '2a4ff86f9aaa70041ec8e82db64abf56'}
    res = requests.get("http://api.openweathermap.org/data/2.5/weather", params)
    res = res.json()

    return f'{city}: {res["weather"][0]["main"]}'

@app.route("/llm/<question>/")
def llm(question: str):
    headers = {"Content-Type": "application/json", 
               "Authorization": "Bearer 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"}
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
# 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
# meta-llama/llama-guard-4-12b