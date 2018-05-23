import requests

url = "https://news.163.com/rank"

response = requests.get(url)
content = requests.get(url).content

print(content.decode("gbk"))

