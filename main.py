from flask import Flask, render_template, request
import requests
from langdetect import detect
from app import LANGUAGES


app = Flask(__name__)



def translate_text(text, to_lang):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': to_lang,
            'dt': 't',
            'q': text
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        return data[0][0][0]
    except:
        return "Ошибка перевода"

@app.route('/', methods=['GET', 'POST'])
def index():
    translation = ""
    selected_lang = "en"
    input_text = ""
    
    if request.method == 'POST':
        input_text = request.form.get('text', '')
        selected_lang = request.form.get('language', 'en')
        
        if input_text:
            translation = translate_text(input_text, selected_lang)
    
    return render_template('index.html', 
                         languages=LANGUAGES,
                         translation=translation,
                         selected_lang=selected_lang,
                         input_text=input_text)

if __name__ == '__main__':
    app.run(debug=True)