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

    @staticmethod
    def get_remote_pokemon(name):
        """
        Get the pokemon from the remote API.
        """
        logging.info(f"Getting remote pokemon: {name}")
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
        logging.info("Getting remote translation for pokemon")
        url = settings.SHAKESPEARE_TRANSLATION_API
        if translation_type == "yoda":
            url = settings.YODA_TRANSLATION_API

        try:
            translation_json = make_request(url, params={"text": description})
            logging.info("Translation json: %s", translation_json)
            result = translation_json["contents"]["translated"]
        except Exception as e:
            logging.info(f"An error occurred: {e}")
            result = None

        return result

    @classmethod
    def retrieve_description(cls, descriptions: List[Dict[str, str]]) -> str:
        """
        Retrieve the description from the list of descriptions.
        """
        logging.info("Parsing data for description")
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
        logging.info("Creating pokemon from remote data")
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
        logging.info("Creating pokemon from dictionary")
        pokemon = dict()
        pokemon["name"] = pokemon_data["name"]
        pokemon["description"] = cls.retrieve_description(
            pokemon_data["flavor_text_entries"]
        )
        pokemon["habitat"] = ""
        if pokemon_data["habitat"]:
            pokemon["habitat"] = pokemon_data["habitat"]["name"]
        pokemon["isLegendary"] = pokemon_data["is_legendary"]
        if translation := pokemon_data.get("translation"):
            pokemon["translation"] = translation

        return Pokemon(**pokemon)

    @classmethod
    def get(cls, name, redis_client=RedisClient):
        """
        Retrieve pokemon
        """
        logging.info("Retrieving pokemon from DB")
        redis_pokemon = redis_client.get(name)
        if not redis_pokemon:
            return cls.create_pokemon_from_remote(name)
        return Pokemon(**json.loads(redis_pokemon))

    @classmethod
    def pokemon_from_json(cls, json_data):
        """
        Create the pokemon from a dictionary.
        """
        logging.info("Creating pokemon from JSON")
        pokemon = cls(
            name=json_data["name"],
            description=json_data["description"],
            habitat=json_data["habitat"],
            isLegendary=json_data["is_legendary"],
        )
        if "translation" in json_data:
            pokemon.translation = json_data["translation"]

        return pokemon

    @property
    def is_yoda_translation(self):
        logging.info(f"Getting translation type for pokemon: {self.name}")
        return self.habitat == "cave" or self.isLegendary

    def save(self):
        """
        Save the pokemon to Redis.
        """
        logging.info("Saving pokemon to DB")
        self.redis_client.set(self.name, json.dumps(self.pokemon_to_dict()))

    def pokemon_to_dict(self):
        """
        Convert the pokemon to a dictionary.
        """
        logging.info(f"Converting pokemon: {self.name} into dict")
        result = {
            "name": self.name,
            "description": self.description,
            "habitat": self.habitat,
            "isLegendary": self.isLegendary,
        }
        if self.translation:
            result["translation"] = self.translation

        return result

    def serialize(self, translate=False):
        logging.info(f"Serializing pokemon: {self.name}")
        result = {
            "name": self.name,
            "habitat": self.habitat,
            "description": self.description,
            "isLegendary": self.isLegendary,
        }
        if translate:
            logging.info(f"Translating pokemon {self.name}")
            result["description"] = self.translation or self.description
            result["translation"] = (
                "Yoda" if self.is_yoda_translation else "Shakespeare"
            )

        logging.info(f"Serialized pokemon: {result}")

        return result
    
    def translate_description(self):
        """
        Translate the pokemon description.
        """
        logging.info(f"Translating pokemon, {self.name} description")
        if self.translation:
            return
        if self.is_yoda_translation:
            logging.info("Translating pokemon to Yoda")
            self.translation = self.get_translation(self.description, "yoda")
        else:
            logging.info("Translating pokemon to Shakespeare")
            self.translation = self.get_translation(self.description, "shakespeare")
