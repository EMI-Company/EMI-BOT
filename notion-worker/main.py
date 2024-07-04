from notion_client import Client
import os

# Ваш интеграционный токен
# URL главной страницы
page_url = ""

# Ваш интеграционный токен
token = ""
# URL главной страницы
page_id = ""

client = Client(auth=token)


def extract_text_from_block(block):
    texts = []
    # texts.append(block['paragraph']['text'][0]['plain_text'])

    if 'rich_text' in block:
        print(block)
        for text in block['rich_text']:
            if 'text' in text:
                texts.append(text['text']['content'])
    return ''.join(texts)


def save_page_content(page_id, folder_path):
    page = client.blocks.children.list(page_id)
    page_title = client.pages.retrieve(
        page_id)['properties']['title']['title'][0]['text']['content']

    # Создаем папку для страницы, если ее нет
    page_folder = os.path.join(folder_path, page_title.replace('/', '_'))
    os.makedirs(page_folder, exist_ok=True)

    # Сохраняем содержимое страницы в текстовый файл
    with open(os.path.join(page_folder, 'content.txt'), 'w', encoding='utf-8') as f:
        f.write(page_title + '\n\n')
        for block in page['results']:
            if block['type'] == 'paragraph':
                text = extract_text_from_block(block['paragraph'])
                f.write(text + '\n')
            elif block['type'] == 'heading_1':
                text = extract_text_from_block(block['heading_1'])
                f.write('# ' + text + '\n')
            elif block['type'] == 'heading_2':
                text = extract_text_from_block(block['heading_2'])
                f.write('## ' + text + '\n')
            elif block['type'] == 'heading_3':
                text = extract_text_from_block(block['heading_3'])
                f.write('### ' + text + '\n')
            elif block['type'] == 'child_page':
                f.write('Child page: ' + block['child_page']['title'] + '\n')

    # Обрабатываем подстраницы
    for block in page['results']:
        if block['type'] == 'child_page':
            save_page_content(block['id'], page_folder)


# Указываем путь для сохранения файлов
save_path = "./"

# Сохраняем содержимое главной страницы и всех подстраниц
save_page_content(page_id, save_path)
