import notion_client

import stevens

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

    def get_page(self, page_id, retrieve_blocks=False):
        return Page.from_id(page_id, retrieve_blocks=retrieve_blocks)

    def get_all_pages(self, entity_type, retrieve_blocks=False):
        pages_json = []
        database_id = entity_type.notion_database_id
        response = CLIENT.databases.query(database_id=database_id)
        pages_json += response['results']
        while response['has_more']:
            response = CLIENT.databases.query(database_id=database_id,
                                              start_cursor=response['next_cursor'])
            pages_json += response['results']
        pages = [Page.from_json(page_json, retrieve_blocks) for page_json in pages_json]
        return pages

    def create_page(self, page_title, entity_type):
        title_property_dict = format_title_as_property_dict(page_title,
                                                            entity_type.notion_title_property)
        parent_dict = {'database_id': entity_type.notion_database_id}
        icon_dict = {'type': 'emoji', 'emoji': entity_type.notion_emoji}
        new_page_json = CLIENT.pages.create(parent=parent_dict,
                                            properties=title_property_dict,
                                            icon=icon_dict)
        new_page = Page.from_json(new_page_json, retrieve_blocks=False)
        return new_page

    def add_entity_relations(self, page, entities):
        entities_by_type = stevens.group_entities_by_type(entities)
        for this_type, this_type_entities in entities_by_type.items():
            this_type_relations = []
            this_type_pages = self.get_all_pages(this_type)
            this_type_pages_by_title = index_pages_by_title(this_type_pages)
            for entity in this_type_entities:
                key = get_title_as_key(entity.name)
                entity_page = this_type_pages_by_title.get(key)
                if not entity_page:
                    entity_page = self.create_page(page_title=entity.name,
                                                   entity_type=this_type)
                this_type_relations.append(entity_page)
            page.add_relations(this_type, this_type_relations)


class Page(object):

    def __init__(self,
                 page_id,
                 page_json,
                 page_title,
                 page_aliases,
                 retrieve_blocks=False):
        self.json = page_json
        self.id = page_id
        self.url = f"https://notion.so/{self.id.replace('-','')}"
        self.title = page_title
        self.aliases = page_aliases
        if retrieve_blocks:
            self.blocks = self.get_blocks()
            self.plaintext = self.get_plaintext()

    @classmethod
    def from_json(cls, page_json, retrieve_blocks=False):
        page_id = page_json['id']
        page_title = page_json['properties']['Name']['title'][0]['plain_text']
        aliases_json = page_json['properties'].get('Aliases')
        if aliases_json and aliases_json['rich_text']:
            aliases_str = aliases_json['rich_text'][0]['plain_text']
            page_aliases = [a.strip() for a in aliases_str.split(',')]
        else:
            page_aliases = []
        return cls(page_id, page_json, page_title, page_aliases, retrieve_blocks)

    @classmethod
    def from_id(cls, page_id, retrieve_blocks=False):
        page_json = CLIENT.pages.retrieve(page_id=page_id)
        return cls.from_json(page_json, retrieve_blocks)

    def __str__(self):
        return f'ID: {self.id} Title: "{self.title}"'

    def __repr__(self):
        return f'<Page {self}>'

    def get_blocks(self):
        if not hasattr(self, 'blocks'):
            self.blocks = CLIENT.blocks.children.list(block_id=self.id)['results']
        return self.blocks

    def get_plaintext(self):
        if not hasattr(self, 'plaintext'):
            plaintext = f'{self.title}\n\n'
            for block in self.get_blocks():
                plaintext += self.get_block_plaintext(block)
            self.plaintext = plaintext
        return self.plaintext.strip()

    def get_block_plaintext(self, block):
        plaintext = ''
        block_type = block['type']
        if block_type in TEXT_BLOCK_TYPES:
            rich_text = block[block_type]['rich_text']
            for text in rich_text:
                plaintext += text['plain_text']
            plaintext += '\n\n'
        return plaintext

    def add_relations(self, entity_type, relations):
        relation_json = self.json['properties'][entity_type.notion_relation_name]
        relation_ids = [{'id': page.id} for page in relations]
        relation_json['relation'] = relation_json['relation'] + relation_ids
        property_update_dict = {entity_type.notion_relation_name: relation_json}
        self.json = CLIENT.pages.update(page_id=self.id,
                                        properties=property_update_dict)


def index_pages_by_title(pages):
    pages_dict = {}
    for page in pages:
        key = get_title_as_key(page.title)
        pages_dict[key] = page
        for alias in page.aliases:
            key = get_title_as_key(alias)
            pages_dict[key] = page
    return pages_dict


def get_title_as_key(title):
    return title.strip().lower()


def format_title_as_property_dict(title, title_property='Name'):
    property_dict = {
        title_property: {
            'title': [
                {
                    'text':
                    {
                        'content': title
                    }
                }
            ]
        }
    }
    return property_dict
