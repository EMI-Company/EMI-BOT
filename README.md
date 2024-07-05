# EMI-BOT
## Инструкция к запуску
- Для успешного запуска нужно присвоить переменные среды в соответствии вашим данным:
пример на язые python
```
os.environ['NOTION_TOKEN'] = 'secret'
os.environ['API_TOKEN'] = 'secret'
os.environ['Ya_API_KEY'] = "secret"
os.environ['FOLDER_ID'] = "secret"
```
- Далее следует устновить зависмости и запустить код по средствам команды:
```
pip install -r requirements.txt
python3 main.py
```
