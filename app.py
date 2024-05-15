import json
import urllib.request
from openai import OpenAI
from flask import Flask, render_template, request

NAVER_API_CLIENT_ID = "네이버 개발자 센터 검색 API"
NAVER_API_CLIENT_SECRET = "네이버 개발자 센터 검색 API"

OPENAI_API_KEY = "OpenAI ChatGPT API"


def search_book(title):
    client_id = NAVER_API_CLIENT_ID
    client_secret = NAVER_API_CLIENT_SECRET

    url = "https://openapi.naver.com/v1/search/book.json"
    query = "?query=" + urllib.parse.quote(title)

    url_query = url + query

    request = urllib.request.Request(url_query)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if (rescode == 200):
        return response.read().decode('utf-8')
    else:
        return None


def parse_book(keyword):
    resp = search_book(keyword)
    if resp is None:
        print("검색 실패!!!")
        exit()

    json_response = json.loads(resp)
    if json_response is None:
        print("json.loads 실패!!!")
        exit()

    data = []
    for item in json_response['items']:
        date = item['pubdate'][:4] + '-' + item['pubdate'][4:6] + '-' + item['pubdate'][6:]
        book = {"image": item['image'], "title": item['title'], "author": item['author'],
                "publisher": item['publisher'], "pubdate": date, "description": item['description'],
                "price": item['discount'] + '원'}
        data.append(book)

    return data


def gpt_recommend(keyword):
    client = OpenAI(api_key=OPENAI_API_KEY)

    content = str(keyword)[1:-1] + "에 관한 책들 추천해줘"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": content}
        ]
    )

    return completion.choices[0].message


app = Flask("Book Recommendation")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search():
    keyword = request.args.get('keyword')
    if keyword is None or keyword == "":
        return render_template("no_input.html")
    data = parse_book(keyword)

    return render_template("search.html", keyword=keyword, data=data)


@app.route("/recommend", methods=['POST', 'GET'])
def recommend():
    keyword = []

    for r in request.args:
        keyword.append(r)

    return render_template("recommend.html", result=gpt_recommend(keyword))


app.run("0.0.0.0")
