import notion_client

DEFAULT_NOTION_KEY = 'notion_secret_key'
with open(DEFAULT_NOTION_KEY) as f:
    KEY = f.readline().strip()
    CLIENT = notion_client.Client(auth=KEY)

TEXT_BLOCK_TYPES = [
    'paragraph',
    'heading_1',
    'heading_2',
    'heading_3',
    'bulleted_list_item',
    'numbered_list_item',
    'to_do',
    'toggle',
    'quote'
]



class NotionController(object):

    def __init__(self, entity_types):
        self.entity_types = entity_types
    
    def get_page(self, page_id):
        return Page(page_id)

    def add_entity_relations(self, page, entities):
        pass
    

class Page(object):

    def __init__(self, page_id):
        self.json = CLIENT.pages.retrieve(page_id=page_id)
        self.id = self.json['id']
        self.title = self.json['properties']['Name']['title'][0]['plain_text']
        self.blocks = self.get_blocks()
        self.plaintext = self.get_plaintext()

    def __str__(self):
        return f'ID: {self.id} Title: "{self.title}"'

    def __repr__(self):
        return f'<Page {self}>'

    def get_blocks(self):
        blocks = CLIENT.blocks.children.list(block_id=self.id)['results']
        return blocks
        
    def get_plaintext(self):
        plaintext = ''
        for block in self.blocks:
            plaintext += self.get_block_plaintext(block)
        return plaintext

    def get_block_plaintext(self, block):
        plaintext = ''
        block_type = block['type']
        if block_type in TEXT_BLOCK_TYPES:
            rich_text = block[block_type]['rich_text']
            for text in rich_text:
                plaintext += text['plain_text']
            plaintext += '\n\n'
        return plaintext
