class Entity(object):

    def __init__(
            self,
            name='',
            entity_type=None,
            json=''
    ):
        self.name = name
        self.entity_type = entity_type
        self.json = json

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'<{self.entity_type} Entity: {self}>'


class EntityType(object):

    def __init__(
            self,
            name='',
            notion_database_id='',
            notion_title_property='',
            notion_relation_name='',
            notion_emoji='',
            openai_response_key='',
    ):
        self.name = name
        self.notion_database_id = notion_database_id
        self.notion_title_property = notion_title_property
        self.notion_relation_name = notion_relation_name
        self.notion_emoji = notion_emoji
        self.openai_response_key = openai_response_key

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'<EntityType {self}, database_id={self.notion_database_id}>'
