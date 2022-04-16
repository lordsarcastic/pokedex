import json
import logging
import random
from typing import Any, Dict, List
from urllib import parse

from django.conf import settings
import redis

import requests

from pokemon.services import make_request


RedisClient = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
logging.basicConfig(level=logging.DEBUG)


class Pokemon:
    POKEMON_LANGUAGE_KEY = "en"

    def __init__(
        self,
        name: str,
        description: str,
        habitat: str,
        isLegendary: bool,
        translation: str = None,
        redis_client: redis.Redis = RedisClient,
    ) -> None:
        self.name = name
        self.description = description
        self.habitat = habitat
        self.isLegendary = isLegendary
        self.translation = translation
        self.redis_client = redis_client

    @property
    def is_yoda_translation(self):
        logging.info("getting translation type")
        return self.habitat == "cave" or self.isLegendary

    

    @staticmethod
    def get_remote_pokemon(name):
        """
        Get the pokemon from the remote API.
        """
        logging.info("getting remote pokemon")
        try:
            pokemon_details = make_request(settings.POKEMON_API_URL + name)
        except requests.exceptions.HTTPError:
            pokemon_details = None

        return pokemon_details

    @staticmethod
    def get_translation(description, translation_type):
        """
        Get the shakespeare translation of the pokemon description.
        """
        logging.info("getting translation")
        url = settings.SHAKESPEARE_TRANSLATION_API
        if translation_type == "yoda":
            settings.YODA_TRANSLATION_API
        endpoint = f"{url}?text={parse.quote(description)}"
        logging.info(endpoint)
        try:
            translation_json = make_request(f"{url}?text={description}")
            if not translation_json.get("success").get("total") < 1:
                raise requests.exceptions.HTTPError("An error occurred")
            result = translation_json["contents"]["translated"]
        except:
            logging.info("An error occurred")
            result = None

        return result

    @classmethod
    def retrieve_description(cls, descriptions: List[Dict[str, str]]) -> str:
        """
        Retrieve the description from the list of descriptions.
        """
        logging.info("getting description")
        english_descriptions = filter(
            lambda desc: desc["language"]["name"] == cls.POKEMON_LANGUAGE_KEY,
            descriptions,
        )

        chosen_description = random.choice([*english_descriptions])
        return chosen_description["flavor_text"]

    @classmethod
    def create_pokemon_from_remote(cls, name):
        """
        Create the pokemon from the remote API.
        """
        logging.info("getting pokemon from remote")
        pokemon_details = cls.get_remote_pokemon(name)
        if not pokemon_details:
            return None

        pokemon = cls.create_pokemon(pokemon_details)
        return pokemon

    @classmethod
    def create_pokemon(cls, pokemon_data: Dict[Any, Any]) -> "Pokemon":
        """
        Convert the remote API data to a pokemon.
        """
        logging.info("getting creating pokemon")
        pokemon = dict()
        pokemon["name"] = pokemon_data["name"]
        pokemon["description"] = cls.retrieve_description(
            pokemon_data["flavor_text_entries"]
        )
        pokemon["habitat"] = pokemon_data.get("habitat").get("name") or ""
        pokemon["isLegendary"] = pokemon_data["is_legendary"]
        if translation := pokemon_data.get("translation"):
            pokemon["translation"] = translation

        return Pokemon(**pokemon)

    def save(self):
        """
        Save the pokemon to Redis.
        """
        logging.info("Saving pokemon to DB")
        self.redis_client.set(
            self.name,
            json.dumps(self.pokemon_to_dict())
        )

    @classmethod
    def get(cls, name, redis_client=RedisClient):
        """
        Retrieve pokemon
        """
        logging.info("getting pokemon")
        redis_pokemon = redis_client.get(name)
        if not redis_pokemon:
            return cls.create_pokemon_from_remote(name)
        return Pokemon(**json.loads(redis_pokemon))

    def pokemon_to_dict(self):
        """
        Convert the pokemon to a dictionary.
        """
        logging.info("getting pokemon into dict")
        result = {
            "name": self.name,
            "description": self.description,
            "habitat": self.habitat,
            "isLegendary": self.isLegendary,
        }
        if self.translation:
            result["translation"] = self.translation

        return result

    def serialize(self):
        logging.info("getting serializerd pokemon")
        result = {
            "name": self.name,
            "description": self.translation or self.description,
            "habitat": self.habitat,
            "isLegendary": self.isLegendary,
        }

        return result

    @classmethod
    def pokemon_from_json(cls, json_data):
        """
        Create the pokemon from a dictionary.
        """
        logging.info("getting pokemon form json")
        pokemon = cls(
            name=json_data["name"],
            description=json_data["description"],
            habitat=json_data["habitat"],
            isLegendary=json_data["is_legendary"]
        )
        if "translation" in json_data:
            pokemon.translation = json_data["translation"]

        return pokemon

    def translate_description(self):
        """
        Translate the pokemon description.
        """
        logging.info("getting pokemon description tranlation")
        if self.translation:
            return
        if self.is_yoda_translation:
            self.translation = self.get_translation(self.description, "yoda")
        else:
            self.translation = self.get_translation(
                self.description, "shakespeare"
            )
