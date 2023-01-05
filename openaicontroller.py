import json
import openai

from entity import Entity

DEFAULT_OPENAI_KEY = 'openai_secret_key'
with open(DEFAULT_OPENAI_KEY) as f:
    KEY = f.readline().strip()
    openai.api_key = KEY
DEFAULT_ENGINE = 'text-davinci-003'
DEFAULT_PROMPTS_FILE = 'prompts.json'


class OpenAIController(object):

    def __init__(
            self,
            entity_types,
            prompts_file=DEFAULT_PROMPTS_FILE,
            engine=DEFAULT_ENGINE
    ):
        self.entity_types = entity_types
        self.engine = engine
        with open(prompts_file) as f:
            self.prompts = json.load(f)
        self.entity_extractor = EntityExtractor(
            prompt_template=self.prompts['entity_extraction'],
            entity_types=self.entity_types,
            engine=self.engine
        )

    def extract_entities(self, text, entity_types):
        entities = self.entity_extractor.extract(text, entity_types)
        return entities



class EntityExtractor(object):

    def __init__(
            self,
            prompt_template,
            entity_types=[],
            engine=DEFAULT_ENGINE
    ):
        self.entity_types = entity_types
        self.prompt_template = prompt_template
        self.engine = engine

    def extract(self, texti, entity_types):
        prompt = self.add_text_to_prompt(text)
        entities_dict = self.run_completion(prompt)
        entities = self.format_entities(entities_dict)

    def add_text_to_prompt(self, text):
        return f"""
        REAL TEXT:
        ###
        {text}
        ###

        REAL OUTPUT:
        """

    def run_completion(self, prompt):
        extraction = openai.Completion.create(
            engine=self.engine,
            prompt=extraction_prompt,
            max_tokens=1024,
            temperature=0.1
        )
        entities_text = extraction['choices'][0]['text']
        return json.loads(entities_text)

    def format_entities(self, entities_dict):
        entities = {}
        for entity_type in self.entity_types:
            this_type_entities = []
            for entity_name in entities_dict[entity_type.openai_response_key]:
                entity = Entity(name=entity_name, entity_type=entity_type)
                this_type_entities.append(entity)
            entities[entity_type] = this_type_entities
        return entities
