from notion_client import Client
from settings import NOTION_TOKEN
import os


class NotionWorker():
    def __init__(self):
        self.client = Client(auth=NOTION_TOKEN)
        self.result = []

    def extract_token_from_url(url):
        parts = url.split('-')
        return parts[-1]

    def extract_text_from_block(self, block):
        texts = []

        if 'rich_text' in block:
            for text in block['rich_text']:
                if 'text' in text:
                    texts.append(text['text']['content'])
        return ''.join(texts)

    def save_page_content(self, page_id, folder_path):
        page = self.client.blocks.children.list(page_id)
        page_title = self.client.pages.retrieve(
            page_id)['properties']['title']['title'][0]['text']['content']

        page_folder = os.path.join(folder_path, page_title.replace('/', '_'))
        os.makedirs(page_folder, exist_ok=True)

        with open(os.path.join(page_folder, 'content.txt'), 'w', encoding='utf-8') as f:
            f.write(page_title + '\n\n')
            for block in page['results']:
                if block['type'] == 'paragraph':
                    text = self.extract_text_from_block(block['paragraph'])
                    f.write(text + '\n')
                elif block['type'] == 'heading_1':
                    text = self.extract_text_from_block(block['heading_1'])
                    f.write('# ' + text + '\n')
                elif block['type'] == 'heading_2':
                    text = self.extract_text_from_block(block['heading_2'])
                    f.write('## ' + text + '\n')
                elif block['type'] == 'heading_3':
                    text = self.extract_text_from_block(block['heading_3'])
                    f.write('### ' + text + '\n')
                elif block['type'] == 'child_page':
                    f.write('Child page: ' +
                            block['child_page']['title'] + '\n')

        # Обрабатываем подстраницы
        for block in page['results']:
            if block['type'] == 'child_page':
                self.save_page_content(block['id'], page_folder)

    def parse_page_content(self, page_id):
        page = self.client.blocks.children.list(page_id)
        page_title = self.client.pages.retrieve(
            page_id)['properties']['title']['title'][0]['text']['content']

        result_accumulator = [page_title + "\n"]

        for block in page['results']:
            if block['type'] == 'paragraph':
                text = self.extract_text_from_block(block['paragraph'])
                result_accumulator.append(text + '\n')
            elif block['type'] == 'heading_1':
                text = self.extract_text_from_block(block['heading_1'])
                result_accumulator.append('# ' + text + '\n')
            elif block['type'] == 'heading_2':
                text = self.extract_text_from_block(block['heading_2'])
                result_accumulator.append('## ' + text + '\n')
            elif block['type'] == 'heading_3':
                text = self.extract_text_from_block(block['heading_3'])
                result_accumulator.append('### ' + text + '\n')

        self.result.append("".join(result_accumulator))

        # Обрабатываем подстраницы
        for block in page['results']:
            if block['type'] == 'child_page':
                self.parse_page_content(block['id'])
