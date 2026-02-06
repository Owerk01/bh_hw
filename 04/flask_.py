import flask
import os
import requests
from functools import wraps
import json
import re
import email_validator
import hashlib
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

# SECRET_KEY=my_secret_key_sadj;ask_dj;askjd9032094u
# GROQ_API_KEY=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
# WEATHER_API_KEY=2a4ff86f9aaa70041ec8e82db64abf56

BASE_DIR = os.path.dirname(__file__)

app = flask.Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, "templates"),
            static_folder=os.path.join(BASE_DIR, "static"))

app.config['SECRET_KEY'] = SECRET_KEY

LOGIN_PATTERN = re.compile(r'^[a-zA-Z0-9_]{6,20}$')
PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,15}$')
NAME_PATTERN = re.compile(r'^[а-яА-Я]+?')

def hash_password(password:str) -> bytes:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + key

def verify_password(hashed_original: str, entered: str) -> bool:
    original = bytes.fromhex(hashed_original)
    hash = original[32:]
    salt = original[:32]
    hashed_entered = hashlib.pbkdf2_hmac('sha256', entered.encode('utf-8'), salt, 100000)
    return original == salt + hashed_entered

def check_login(login: str) -> bool:
    if LOGIN_PATTERN.search(login):
        return True
    else:
        return False

def check_password(password: str) -> bool:
    if PASSWORD_PATTERN.search(password):
        return True
    else:
        return False
    
def check_exist(login: str) -> bool:
    with open(f"{BASE_DIR}/users.json", "r") as f:
        users = json.load(f)
    
    return any(user["login"] == login for user in users)
    
def check_names(name: str) -> bool:
    if NAME_PATTERN.search(name):
        return True
    else:
        return False
    
def check_form(first_name: str, last_name: str, age: int, email: str, login: str, password: str) -> list:
    errors = []
    
    if not check_names(first_name):
            errors.append("Имя должно содержать только русские буквы")
    if not check_names(last_name):
        errors.append("Фамилия должна  содержать только русские буквы")
    try:
        age = int(age)
    except:
        errors.append("Поле возраста должно содержать число!")
    else:
        if age < 12 or age > 100:
            errors.append("Возраст должен быть от 12 до 100 лет")
    try:
        validated_email = email_validator.validate_email(email)
        email = validated_email.email
    except email_validator.EmailNotValidError as e:
        errors.append(f"Некорректный email: {e}")
    if not check_login(login):
        errors.append("Логин может состоять только из символов латинского алфавита, цифр и нижнего подчёркивания и должен содержать от 6 до 20 символов")
    if not check_password(password):
        errors.append("Пароль должен содержать хотя бы одну латинскую заглавную и прописную букву, цифру и содержать от 8 до 15 символов")
    if check_exist(login):
        errors.append("Пользователь с таким логином уже существует")

    return errors

def save_user(first_name: str, last_name: str, age: int, email: str, login: str, password: str):
    with open(f"{BASE_DIR}/users.json", "r") as f:
        data = json.load(f)

    password = hash_password(password).hex()

    data.append({"first_name": first_name, 
                 "last_name": last_name, 
                 "age": age, 
                 "email": email, 
                 "login": login,
                 "password": password})
    
    with open(f"{BASE_DIR}/users.json", "w") as f:
        json.dump(data, f, indent=2)

def get_user_by_login(login: str):
    try:
        with open(f"{BASE_DIR}/users.json", 'r') as f:
            users = json.load(f)
        for user in users:
            if user["login"] == login:
                return user
    except:
        pass
    return None

def only_authorized(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not flask.session.get("login"): 
            return flask.redirect(flask.url_for('login'))
        return f(*a, **kw)
    return wrapper

@app.route('/login/', methods=['post', 'get'])
def login():
    errors = []

    if flask.request.method == 'POST':
        login = flask.request.form.get("login")
        password = flask.request.form.get("password")

        if not login:
            errors.append("Вы не ввели логин")
        elif not password:
            errors.append("Вы не ввели пароль")
        else:
            user = get_user_by_login(login)
            if user == None:
                errors.append("Пользователя с таким логином не существует")
            elif not verify_password(hashed_original=user["password"], entered=password):
                errors.append("Неверный пароль")
            else: 
                flask.session["login"] = login
                flask.session["full_name"] = user["first_name"] + " " + user["last_name"]
                return flask.redirect(flask.url_for("index"))
    
    return flask.render_template('login.html', errors=errors)

@app.route('/logout')
@only_authorized
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for("login"))

@app.route('/register/', methods=["post", "get"])
def register():
    if not os.path.exists(f"{BASE_DIR}/users.json"):
        with open(f"{BASE_DIR}/users.json", "w", encoding="utf-8") as f:
            json.dump([], f)

    errors = []
    data = {}
    if flask.request.method == "POST":
        data["first_name"] = flask.request.form.get('first_name', '').strip()
        data["last_name"] = flask.request.form.get('last_name', '').strip()
        data["age"] = flask.request.form.get('age', '').strip()
        data["email"] = flask.request.form.get('email', '').strip()
        data["login"] = flask.request.form.get('login', '').strip()
        data["password"] = flask.request.form.get('password', '').strip()
        
        errors = check_form(**data)

        if errors == []:
            save_user(**data)
            return flask.redirect(flask.url_for("login"))

    return flask.render_template('register.html', errors=errors)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route("/duck/")
@only_authorized
def duck():
    res = requests.get("https://random-d.uk/api/random")
    res = res.json()
    url = res["url"]
    num = url.split('/')[-1].split('.')[0]
    return flask.render_template('duck.html', num=num, url=url)

@app.route("/foxes/", methods=['post', 'get'])
@only_authorized
def foxes():
    error = ''
    foxes = []

    if flask.request.method == 'POST':
        num = flask.request.form.get('num', '').strip()

        try:
            num = int(num)
        except:
            error = "Количество лисичек должно быть числом"
        else:
            if num < 1 or num > 10:
                error = "Количесто лисичек должно быть от 1 до 10"

            for _ in range(num):
                res = requests.get("https://randomfox.ca/floof")
                res = res.json()
                image = res["image"]
                pic_num = image.split('/')[-1].split('.')[0]
                foxes.append({"num": pic_num, "url": image})
    return flask.render_template("foxes.html", foxes=foxes, error=error, submitted=bool(foxes or error))

@app.route('/weather/', methods=['post', 'get'])
@only_authorized
def weather():
    error = ''
    city = ''
    context = ''
    if flask.request.method == 'POST':
        city = flask.request.form.get('city', '').strip().lower()
        if not city:
            error = "Вы не ввели город"
        elif city == "minsk":
            pass
        else:
            try:
                params = {'q': f"{city}", f'APPID': {WEATHER_API_KEY}, 'units': 'metric'}
                res = requests.get("http://api.openweathermap.org/data/2.5/weather", params)
                res = res.json()
                
                context = {
                    'city': res['name'],
                    'temp_c': res['main']['temp'],
                    'feels_like_c': res['main']['feels_like'],
                    'description': res['weather'][0]['description'],
                    'humidity': res['main']['humidity'],
                    'pressure': res['main']['pressure'],
                    'wind_speed': res['wind']['speed'],
                    'wind_deg': res['wind']['deg'],
                    'visibility': res.get('visibility', 0),
                    'country': res['sys']['country'],
                    'icon': res['weather'][0]['icon']
                }
            except:
                error = "Something went wrong"
    return flask.render_template('weather.html',
                                 error=error,
                                 city=city,
                                 is_minsk=True if city == "minsk" else False,
                                 weather=context)

@app.route('/llm/', methods=["post", "get"])
@only_authorized
def llm():
    error = ''
    answer = ''
    question = ''
    if flask.request.method == "POST":
        question = flask.request.form.get('question')

        if not question:
            error = "Вы не ввели запрос"
        else:
            headers = {"Content-Type": "application/json", 
                    "Authorization": f"Bearer {GROQ_API_KEY}"}
            data = {"model": "llama-3.3-70b-versatile",
                    "messages": [{
                        "role": "user",
                        "content": f"{question}"
                    }]
                    }
            try:
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
                answer = res.json()["choices"][0]["message"]["content"]
            except:
                error = f"Что-то не так: {res.json()["error"]["code"]}"
    return flask.render_template("llm.html", error=error, answer=answer, question=question)

@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template("error.html", error=error)

app.run(debug=True, host='0.0.0.0')