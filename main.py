from flask import Flask, render_template, request
import requests

from app import LANGUAGES


app = Flask(__name__)



def translate_text(text, to_lang):
   
    if not text.strip():
        return ""

    try:
        # 1. Разбиваем исходный текст на абзацы
        paragraphs = text.split('\n')
        translated_paragraphs = []  # Сюда будем складывать переводы каждого абзаца
        # 2. Перебираем каждый абзац и переводим его
        for paragraph in paragraphs:
            # Если абзац пустой (много переносов подряд), просто добавляем пустую строку
            if not paragraph.strip():
                translated_paragraphs.append("")
                continue

            # URL и параметры для запроса к Google Translate API
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': to_lang,
                'dt': 't',
                'q': paragraph
            }

            # Отправляем запрос для перевода одного абзаца
            response = requests.get(url, params=params)
            response.raise_for_status()  # Проверяем, не было ли ошибки HTTP
            data = response.json()

            # 3. Собираем перевод для текущего абзаца
            translated_text = ""
            # Проверяем, что data[0] существует и является списком
            if data and isinstance(data[0], list):
                for sentence in data[0]:
                    # Извлекаем переведенный текст из каждой части
                    if sentence and isinstance(sentence, list) and len(sentence) > 0:
                        translated_text += sentence[0] or ""  # Добавляем перевод, если он есть

            # Если не удалось получить перевод, используем исходный абзац (или можно вернуть ошибку)
            translated_paragraphs.append(translated_text if translated_text else paragraph)

        # 4. Собираем все переведенные абзацы обратно в один текст, 
        # соединяя их символом новой строки
        
        final_translation = '\n'.join(translated_paragraphs)
        
    
        # НОВЫЙ КОД: Преобразуем в HTML с тегами <p>
        html_paragraphs = []
        for p in translated_paragraphs:
            if p.strip():  # Если абзац не пустой
                html_paragraphs.append(f"<p>{p}</p>")
            else:
                # Для пустых строк можно вставить <br> или оставить пустой абзац <p></p>
                html_paragraphs.append("<p><br></p>")

        # Возвращаем готовый HTML
        return ''.join(html_paragraphs)

    except requests.exceptions.RequestException as e:
        
        print(f"Ошибка сети: {e}")
        return f"Ошибка перевода: проблема с сетью или запросом. {e}"
    except (IndexError, KeyError, TypeError, ValueError) as e:
        # Обработка ошибок парсинга JSON (неожиданная структура)
        print(f"Ошибка парсинга ответа: {e}.")
        return "Ошибка перевода: не удалось обработать ответ сервера"
    except Exception as e:
        print(f"Неизвестная ошибка при переводе: {e}")
        return "Произошла неизвестная ошибка при переводе."

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

app.run(debug=True)