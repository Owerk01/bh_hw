import requests

url = "http://127.0.0.1:8000/users"
data = {"name": "Aleks", "age": 18}
res = requests.post(url, json=data)
print(res.json())
print(res.text)



# for i in range(100):
#      p = {'name':f"user_{i}", 'age':33}
#      res = requests.post("http://127.0.0.1:8000/users", params=p)
#      print(res.text)