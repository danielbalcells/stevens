import json
import openai

from entity import Entity

DEFAULT_OPENAI_KEY = 'openai_secret_key'
with open(DEFAULT_OPENAI_KEY) as f:
    KEY = f.readline().strip()
    openai.api_key = KEY
DEFAULT_ENGINE = 'text-davinci-003'
DEFAULT_PROMPTS_FILE = 'prompts.json'
PROMPT_CHUNK_LEN_CHARS = 10000


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

    def extract_entities(self, text):
        entities = self.entity_extractor.extract(text)
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

    def extract(self, text):
        entities = []
        text_chunks = split_string_by_chunk_size(text, PROMPT_CHUNK_LEN_CHARS)
        for text_chunk in text_chunks:
            prompt = self.add_text_to_prompt(text_chunk)
            entities_dict = self.run_completion(prompt)
            chunk_entities = self.format_entities(entities_dict)
            entities += chunk_entities
        return entities

    def add_text_to_prompt(self, text):
        return self.prompt_template + f"""
        REAL TEXT:
        ###
        {text}
        ###

        REAL OUTPUT:
        """

    def run_completion(self, prompt):
        extraction = openai.Completion.create(
            engine=self.engine,
            prompt=prompt,
            max_tokens=1024,
            temperature=0.1
        )
        entities_text = extraction['choices'][0]['text']
        return json.loads(entities_text)

    def format_entities(self, entities_dict):
        entities = []
        for entity_type in self.entity_types:
            for entity_name in entities_dict[entity_type.openai_response_key]:
                entity = Entity(name=entity_name, entity_type=entity_type)
                entities.append(entity)
        return entities

def split_string_by_chunk_size(string, chunk_size=PROMPT_CHUNK_LEN_CHARS):
    return [string[i:i+chunk_size] for i in range(0, len(string), chunk_size)]
