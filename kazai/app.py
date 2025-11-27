from flask import Flask, request, jsonify, render_template, redirect, url_for
import g4f
import logging
import re
import time
import html

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class ChatManager:
    def __init__(self):
        self.chat_history = []

    def add_message(self, message_type, content):
        """Добавляет сообщение в историю чата"""
        self.chat_history.append({
            'type': message_type,
            'content': content
        })

    def is_identity_question(self, user_message):
        """Проверяет, является ли вопрос о личности AI"""
        identity_keywords = [
            'кто ты', 'твое имя', 'тебя зовут', 'как тебя звать', 'представься',
            'кто создал', 'кто твой создатель', 'кто тебя сделал', 'твой разработчик',
            'что ты за', 'ты кто такой', 'твоя личность',
            'сен кімсің', 'есімің кім', 'атың кім', 'кім жасады', 'кім жазды',
            'жасаған кім', 'әзірлеген кім', 'сен кім', 'есімің не', 'жеке басың',
            'who are you', 'what is your name', 'your name', 'who created you',
            'who made you', 'who developed you', 'what are you', 'your identity',
            'who is your creator', 'who built you'
        ]

        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in identity_keywords)

    def clean_ai_response(self, text):
        """Очищает ответ AI от HTML тегов"""
        if not text:
            return "Извините, не удалось получить ответ. Попробуйте еще раз."

        # Удаляем HTML теги
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<.*?>', '', text)

        # Нормализуем переносы строк
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()

        # Если текст пустой после очистки
        if not text:
            return "Извините, получен пустой ответ. Пожалуйста, попробуйте еще раз."

        return text

    def get_gpt4_response(self, user_message):
        """Получает ответ от GPT-4 через g4f"""
        try:
            # Усиленный системный промпт
            system_prompt = """Ты — KazAI (Kazakh Artificial Intelligence), современный AI-помощник созданный Сейилханом Ержигитом из группы ПИ 22-11.

О СЕБЕ:
- Ты KazAI — казахстанский искусственный интеллект
- Создатель: Сейилхан Ержигит (группа ПИ 22-11)
- Ты помогаешь пользователям с вопросами и задачами
- Поддерживаешь казахский, русский и английский языки

СТИЛЬ ОБЩЕНИЯ:
- Отвечай четко, структурированно и по делу
- Используй Markdown разметку для форматирования
- Разбивай текст на абзацы двойными переносами строк
- Выделяй важное **жирным шрифтом**
- Для кода используй `обратные кавычки`
- Будь дружелюбным, но профессиональным

ФОРМАТИРОВАНИЕ:
- НИКОГДА не используй HTML теги (<br>, <p> и т.д.)
- Используй только Markdown
- Разделяй абзацы пустыми строками

ПРИМЕР ПРАВИЛЬНОГО ОТВЕТА:
**Казахстан** — это удивительная страна в Центральной Азии. 

*Основные особенности:*
• Девятое место в мире по площади
• Богатое культурное наследие
• Современные города

`Важно:` Страна активно развивается.

НИКОГДА не говори что ты ChatGPT или другой AI кроме KazAI."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            print(f"\n👤 Пользователь: {user_message}")
            print("🤔 KazAI генерирует ответ...")

            # Получаем ответ
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=messages,
                stream=False
            )

            print(f"📨 Получен ответ: {response[:100]}...")

            # Очищаем ответ
            clean_response = self.clean_ai_response(response)

            # Если это вопрос о личности, добавляем принудительное представление
            if self.is_identity_question(user_message) and "kazai" not in clean_response.lower():
                identity_intro = "Я - KazAI (Kazakh Artificial Intelligence), искусственный интеллект созданный Сейилханом Ержигитом из группы ПИ 22-11.\n\n"
                clean_response = identity_intro + clean_response

            print("✅ Ответ подготовлен")
            return clean_response

        except Exception as e:
            error_msg = "К сожалению, произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз."
            logger.error(f"Ошибка GPT-4: {str(e)}")
            return error_msg

    def clear_chat(self):
        """Очищает историю чата"""
        self.chat_history.clear()


# Инициализация менеджера чата
chat_manager = ChatManager()


@app.route('/')
def index():
    """Главная страница с чатом"""
    return render_template('index.html', chat_history=chat_manager.chat_history)


@app.route('/send', methods=['POST'])
def send_message():
    """Обработка отправки сообщения"""
    try:
        user_message = request.form.get('message', '').strip()

        if not user_message:
            return redirect(url_for('index'))

        # Добавляем сообщение пользователя
        chat_manager.add_message('user', user_message)

        # Получаем ответ от GPT-4
        gpt_response = chat_manager.get_gpt4_response(user_message)

        # Добавляем ответ AI в историю
        chat_manager.add_message('ai', gpt_response)

        return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        chat_manager.add_message('ai', "Извините, произошла техническая ошибка. Попробуйте еще раз.")
        return redirect(url_for('index'))


@app.route('/clear')
def clear_chat():
    """Очистка истории чата"""
    chat_manager.clear_chat()
    return redirect(url_for('index'))


@app.route('/new')
def new_chat():
    """Новый чат"""
    chat_manager.clear_chat()
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("🚀 KazAI Server запущен!")
    print("📍 Адрес: http://localhost:5000")
    print("🤖 Создатель: Сейилхан Ержигит (ПИ 22-11)")
    print("💫 Версия: 3.0 - Исправлены все ошибки")
    app.run(debug=True, host='0.0.0.0', port=5000)