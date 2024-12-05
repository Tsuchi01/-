import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sqlite3
import http.client
import json
import time


# Клас для інтеграції з моделью T5 через API
class T5Helper:
    def init(self, api_url="api-inference.huggingface.co", api_token="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"):
        self.api_url = api_url  # URL API моделі
        self.api_token = api_token  # Токен авторизації

    # Запит до API для отримання відповіді на промт
    def query(self, prompt):
        conn = http.client.HTTPSConnection(self.api_url)
        payload = json.dumps({"inputs": prompt})
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        try:
            conn.request("POST", "/models/t5-large", payload, headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            if res.status == 200:
                return json.loads(data)
            elif res.status == 503:
                # Если модель еще загружается, ждем и пытаемся снова
                print("Модель ще завантажується, повторюємо запит...")
                time.sleep(10)
                return self.query(prompt)
            else:
                return {"error": data, "status_code": res.status}
        except Exception as e:
            return {"error": str(e), "status_code": 500}

    # Генерація рекомендацій для списка завдань
    def generate_suggestions(self, tasks):
        if not tasks:
            return "Немає завдань для аналізу."

        recommendations = []
        for task in tasks:
            task_id, title, description, deadline, completed, priority = task

            # Покращений промт для отримання більш детальних рекомендацій
            prompt = f"""
            Завдання: "{title}"
            Опис завдання: {description}
            Дедлайн: {deadline}
            Пріоритет: {priority} (1 - найвищий, 5 - найнижчий)

            Задача: на основі цього завдання, надайте рекомендації щодо кроків для досягнення успіху:
            1. Як організувати час для виконання цього завдання?
            2. Як можна зменшити складність завдання?
            3. Як визначити, коли завдання буде виконано вчасно?
            """

            response = self.query(prompt)

            # Перевірка на помилки у відповіді
            if "error" in response:
                recommendations.append(f"Помилка для '{title}': {response['error']}")
            else:
                print(f"Response for task '{title}': {response}")  # Виводимо всю відповідь для налагодження

                # Перевірка на наявність тексту в відповіді
                generated_text = None
                if isinstance(response, list) and len(response) > 0:
                    if 'generated_text' in response[0]:
                        generated_text = response[0]['generated_text']

                if generated_text:
                    recommendations.append(f"Завдання: {title}\nРекомендація: {generated_text}\n")
                else:
                    recommendations.append(f"Завдання: {title}\nРекомендація: (Текст не знайдений у відповіді)\n")

        return "\n".join(recommendations) if recommendations else "Не вдалося отримати рекомендації для завдань."


# Клас для управління завданнями
class TaskManager:
    def init(self):
        self.db_name = "tasks.db"
        self.tasks = []
        self.create_db()

    def create_db(self):
        # Створення або підключення до бази даних
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                deadline TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                priority INTEGER NOT NULL DEFAULT 3
            )
        """)