import json

from notioncontroller import NotionController
from openaicontroller import OpenAIController
from entity import EntityType

DEFAULT_OPENAI_KEY = 'openai_secret_key'
DEFAULT_ENTITY_TYPES = 'entity_types.json'


class Stevens(object):

    def __init__(self, entity_types=DEFAULT_ENTITY_TYPES):
        self.entity_types = self.load_entity_types(entity_types)
        self.notion = NotionController(self.entity_types)
        self.openai = OpenAIController(self.entity_types)

    def load_entity_types(self, entity_types):
        with open(entity_types) as f:
            entity_types_dict = json.load(f)
        entity_types = []
        for type_name, type_values in entity_types_dict.items():
            entity_type = EntityType(
                name=type_name,
                notion_database_id=type_values['notion_database_id'],
                notion_title_property=type_values['notion_title_property'],
                notion_relation_name=type_values['notion_relation_name'],
                notion_emoji=type_values['notion_emoji'],
                openai_response_key=type_values['openai_response_key']
            )
            entity_types.append(entity_type)
        return entity_types

    def tag_page_entities(self, page_id):
        page = self.notion.get_page(page_id)
        entities = self.openai.extract_entities(page.plaintext)
        self.notion.add_entity_relations(page, entities)
