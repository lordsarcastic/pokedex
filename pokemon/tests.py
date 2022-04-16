import json
from typing import Dict
from mock import patch

from rest_framework.test import APITestCase

from pokemon.models import Pokemon


class PokemonRetrieveViewTest(APITestCase):
    def test_pokemon_with_cave_habitat_will_have_yoda_translation(self):
        pokemon = Pokemon(
            name="Pikachu",
            description="A cute electric mouse",
            habitat="cave",
            isLegendary=False,
        )
        self.assertTrue(pokemon.is_yoda_translation)

    def test_pokemon_with_legendary_status_will_have_yoda_translation(self):
        pokemon = Pokemon(
            name="Pikachu",
            description="A cute electric mouse",
            habitat="cave",
            isLegendary=True,
        )
        self.assertTrue(pokemon.is_yoda_translation)

    def test_pokemon_without_legendary_status_and_not_cave_habitat_will_not_have_yoda_translation(self):
        pokemon = Pokemon(
            name="Pikachu",
            description="A cute electric mouse",
            habitat="forest",
            isLegendary=False,
        )
        self.assertFalse(pokemon.is_yoda_translation)

    def test_pokemon_without_cave_habitation_will_not_have_yoda_translation(self):
        pokemon = Pokemon(
            name="Pikachu",
            description="A cute electric mouse",
            habitat="forest",
            isLegendary=False,
        )
        self.assertFalse(pokemon.is_yoda_translation)

    def test_get_remote_pokemons_will_return_pokemon_from_remote(self):
        with patch("pokemon.models.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "name": "Pikachu",
                "flavor_text_entries": [
                    {
                        "language": {"name": "en"},
                        "flavor_text": "A cute electric mouse",
                    },
                    {
                        "language": {"name": "es"},
                        "flavor_text": "Un ratón electrico adorable",
                    },
                ],
                "habitat": {
                    "name": "cave",
                    "url": "https://pokeapi.co/api/v2/growth-rate/4/"
                },
                "is_legendary": False,
            }
            pokemon = Pokemon.get_remote_pokemon("Pikachu")

        self.assertIn("name", pokemon)
        self.assertIn("flavor_text_entries", pokemon)
        self.assertIn("habitat", pokemon)
        self.assertIn("is_legendary", pokemon)

    def test_get_shakespeare_translation_will_return_translation_from_remote(self):
        with patch("pokemon.models.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "success": {"total": 1},
                "contents": {
                    "translated": "From the time 't is born,  a flame burns at the tip of its tail. Its life would end if 't be true the flame wast to wend out.",
                    "text": "From the time it is born, a flame burns at the tip of its tail. Its life would end if the flame were to go out.",
                    "translation": "shakespeare",
                },
            }
            pokemon = Pokemon.get_remote_pokemon("Pikachu")

        self.assertIn("success", pokemon)
        self.assertIn("contents", pokemon)
        self.assertEqual("shakespeare", pokemon["contents"]["translation"])

    def test_get_yoda_translation_will_return_translation(self):
        with patch("pokemon.models.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "success": {"total": 1},
                "contents": {
                    "translated": "From the time 't is born,  a flame burns at the tip of its tail. Its life would end if 't be true the flame wast to wend out.",
                    "text": "From the time it is born, a flame burns at the tip of its tail. Its life would end if the flame were to go out.",
                    "translation": "yoda",
                },
            }
            pokemon = Pokemon.get_remote_pokemon("Pikachu")

        self.assertIn("success", pokemon)
        self.assertIn("contents", pokemon)
        self.assertIn("yoda", pokemon["contents"]["translation"])

    def test_retrieve_description_will_pull_out_description_from_api_response(self):
        with patch("pokemon.models.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "name": "Pikachu",
                "flavor_text_entries": [
                    {
                        "language": {"name": "en"},
                        "flavor_text": "A cute electric mouse",
                    },
                    {
                        "language": {"name": "es"},
                        "flavor_text": "Un ratón electrico adorable",
                    },
                ],
                "habitat": {
                   "name": "cave",
                   "url": "https://pokeapi.co/api/v2/growth-rate/4/"
                },
                "is_legendary": False,
            }
            pokemon = Pokemon.get_remote_pokemon("Pikachu")

        description = Pokemon.retrieve_description(pokemon["flavor_text_entries"])
        self.assertEqual(description, pokemon["flavor_text_entries"][0]["flavor_text"])

    def test_retrieve_description_will_pull_out_description_from_list_from_api_response(
        self,
    ):
        with patch("pokemon.models.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "name": "Pikachu",
                "flavor_text_entries": [
                    {
                        "language": {"name": "en"},
                        "flavor_text": "A cute electric mouse",
                    },
                    {
                        "language": {"name": "en"},
                        "flavor_text": "A cute electric mouse",
                    },
                    {
                        "language": {"name": "en"},
                        "flavor_text": "A cute electric mouse",
                    },
                    {
                        "language": {"name": "es"},
                        "flavor_text": "Un ratón electrico adorable",
                    },
                ],
                "habitat": {
                   "name": "cave",
                   "url": "https://pokeapi.co/api/v2/growth-rate/4/"
                },
                "is_legendary": False,
            }
            pokemon = Pokemon.get_remote_pokemon("Pikachu")

        description = Pokemon.retrieve_description(pokemon["flavor_text_entries"])
        self.assertEqual(description, pokemon["flavor_text_entries"][0]["flavor_text"])

    def test_creating_pokemon_from_remote_will_yield_pokemon(self):
        with patch("pokemon.models.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "name": "Pikachu",
                "flavor_text_entries": [
                    {
                        "language": {"name": "en"},
                        "flavor_text": "A cute electric mouse",
                    },
                    {
                        "language": {"name": "es"},
                        "flavor_text": "Un ratón electrico adorable",
                    },
                ],
                "habitat": {
                    "name": "cave",
                    "url": "https://pokeapi.co/api/v2/growth-rate/4/"
                },
                "is_legendary": False,
            }
            pokemon = Pokemon.create_pokemon_from_remote("Pikachu")

        self.assertEqual(pokemon.name, "Pikachu")
        self.assertEqual(pokemon.description, "A cute electric mouse")
        self.assertEqual(pokemon.habitat, "cave")
        self.assertEqual(pokemon.isLegendary, False)
        self.assertEqual(pokemon.translation, None)

    def test_creating_pokemon_from_dict_will_yield_pokemon(self):
        pokemon_dict = {
            "name": "Pikachu",
            "flavor_text_entries": [
                {
                    "language": {"name": "en"},
                    "flavor_text": "A cute electric mouse",
                },
                {
                    "language": {"name": "es"},
                    "flavor_text": "Un ratón electrico adorable",
                },
            ],
            "habitat": {
                "name": "cave",
                "url": "https://pokeapi.co/api/v2/growth-rate/4/"
            },
            "is_legendary": False,
        }
        pokemon = Pokemon.create_pokemon(pokemon_dict)

        self.assertEqual(pokemon.name, "Pikachu")
        self.assertEqual(pokemon.description, "A cute electric mouse")
        self.assertEqual(pokemon.habitat, "cave")
        self.assertEqual(pokemon.isLegendary, False)
        self.assertEqual(pokemon.translation, None)

        pokemon_dict["translation"] = "shakespeare"
        pokemon = Pokemon.create_pokemon(pokemon_dict)
        self.assertEqual(pokemon.translation, "shakespeare")

    def test_redis_cache_can_work_for_save_method(self):
        pikachu_dict = {
            "name": "Pikachu",
            "description": "A cute electric mouse",
            "habitat": "cave",
            "isLegendary": False,
        }
        pokemon = Pokemon(**pikachu_dict)
        pokemon.save()
        self.assertEqual(
            pokemon.redis_client.get(pikachu_dict["name"]).decode("utf-8"),
            json.dumps(pokemon.pokemon_to_dict()),
        )
        pokemon.redis_client.delete(pikachu_dict["name"])

    def test_get_method_will_return_pokemon(self):
        with patch("pokemon.models.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {
                "name": "Pikachu",
                "flavor_text_entries": [
                    {
                        "language": {"name": "en"},
                        "flavor_text": "A cute electric mouse",
                    },
                    {
                        "language": {"name": "es"},
                        "flavor_text": "Un ratón electrico adorable",
                    },
                ],
                "habitat": {
                    "name": "cave",
                    "url": "https://pokeapi.co/api/v2/growth-rate/4/"
                },
                "is_legendary": False,
            }

            pokemon = Pokemon.get("Pikachu")
            self.assertEqual(pokemon.name, "Pikachu")
            self.assertEqual(pokemon.description, "A cute electric mouse")
            self.assertEqual(pokemon.habitat, "cave")
            self.assertEqual(pokemon.isLegendary, False)

    def test_pokemon_can_be_created_from_json(self):
        pokemon = Pokemon.pokemon_from_json(
            {
                "name": "Pikachu",
                "description": "A cute electric mouse",
                "habitat": "cave",
                "is_legendary": False,
            }
        )
        self.assertEqual(pokemon.name, "Pikachu")
        self.assertEqual(pokemon.description, "A cute electric mouse")
        self.assertEqual(pokemon.habitat, "cave")
        self.assertFalse(pokemon.isLegendary)
        self.assertIsNone(pokemon.translation)

        pokemon = Pokemon.pokemon_from_json(
            {
                "name": "Pikachu",
                "description": "A cute electric mouse",
                "habitat": "cave",
                "is_legendary": False,
                "translation": "Un ratón electrico adorable",
            }
        )
        self.assertEqual(pokemon.name, "Pikachu")
        self.assertEqual(pokemon.description, "A cute electric mouse")
        self.assertEqual(pokemon.habitat, "cave")
        self.assertEqual(pokemon.isLegendary, False)
        self.assertEqual(pokemon.translation, "Un ratón electrico adorable")

    def test_pokemon_to_dict_will_yield_valid_dict(self):
        pokemon = Pokemon.pokemon_from_json(
            {
                "name": "Pikachu",
                "description": "A cute electric mouse",
                "habitat": "cave",
                "is_legendary": False,
            }
        )
        self.assertEqual(
            pokemon.pokemon_to_dict(),
            {
                "name": "Pikachu",
                "description": "A cute electric mouse",
                "habitat": "cave",
                "isLegendary": False
            }
        )

    def test_pokemon_serialize_will_yield_api_valid_pokemon(self):
        pokemon = Pokemon.pokemon_from_json(
            {
                "name": "Pikachu",
                "description": "A cute electric mouse",
                "habitat": "cave",
                "is_legendary": False,
            }
        )
        self.assertEqual(
            pokemon.serialize(),
            {
                "name": "Pikachu",
                "description": "A cute electric mouse",
                "habitat": "cave",
                "isLegendary": False,
            },
        )
        pokemon = Pokemon.pokemon_from_json(
            {
                "name": "Pikachu",
                "description": "A cute electric mouse",
                "habitat": "cave",
                "is_legendary": False,
                "translation": "Un ratón electrico adorable",
            }
        )
        self.assertEqual(
            pokemon.serialize(),
            {
                "name": "Pikachu",
                "description": "Un ratón electrico adorable",
                "habitat": "cave",
                "isLegendary": False,
            }
        )

    # def test_translate_pokemon_description_will_mutate_translation(self):
    #     with patch("pokemon.models.requests.get") as mock_get:
    #         mock_get.return_value.json.return_value = {
    #             "success": {"total": 1},
    #             "contents": {
    #                 "translated": "From the time 't is born,  a flame burns at the tip of its tail. Its life would end if 't be true the flame wast to wend out.",
    #                 "text": "From the time it is born, a flame burns at the tip of its tail. Its life would end if the flame were to go out.",
    #                 "translation": "shakespeare",
    #             },
    #         }
    #         pokemon = Pokemon.pokemon_from_json(
    #             {
    #                 "name": "Pikachu",
    #                 "description": "A cute electric mouse",
    #                 "habitat": "cave",
    #                 "is_legendary": False,
    #             }
    #         )
    #         print(pokemon.description)
    #         print(pokemon.translation)
    #         pokemon.translate_description()
    #         self.assertEqual(
    #             pokemon.translation,
    #             "From the time 't is born,  a flame burns at the tip of its tail. Its life would end if 't be true the flame wast to wend out.",
    #         )

    # def test_get_pokemon_not_found(self):
    #     with patch("pokemon.models.requests.get") as mock_get:
    #         mock_get.return_value.json.return_value = {
    #             "name": "Pikachu",
    #             "flavor_text_entries": [
    #                 {
    #                     "language": {"name": "en"},
    #                     "flavor_text": "A cute electric mouse",
    #                 },
    #                 {
    #                     "language": {"name": "es"},
    #                     "flavor_text": "Un ratón electrico adorable",
    #                 },
    #             ],
    #             "habitat": {
    #                 "name": "cave",
    #                 "url": "https://pokeapi.co/api/v2/growth-rate/4/"
    #             },
    #             "is_legendary": False,
    #         }

    #         response = self.client.get("/pokemon/non-existent")
    #     print(response.data)
    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(response.data, {"detail": "Pokemon not found"})

    # def test_get_pokemon_found(self):
    #     response = self.client.get("/pokemon/bulbasaur")
    #     print(response.data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("name", response.data)
    #     self.assertIn("description", response.data)
    #     self.assertIn("habitat", response.data)
    #     self.assertIn("isLegendary", response.data)
