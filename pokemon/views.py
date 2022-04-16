from rest_framework.response import Response
from rest_framework.views import APIView

from pokemon.models import Pokemon
from pokemon.serializers import PokemonSerializer



class PokemonRetrieveView(APIView):
    

    def get(self, request, pokemon_name):
        redis_pokemon = Pokemon.get(pokemon_name)
        if not redis_pokemon:
            return Response(
                data={"detail": "Pokemon not found"},
                status=404
            )
        
        redis_pokemon.save()
        serializer = PokemonSerializer(data=redis_pokemon.serialize())
        if serializer.is_valid():
            return Response(
                data=serializer.data,
                status=200
            )
        return Response(
            data=serializer.errors,
            status=400
        )
        


class PokemonTranslateView(APIView):
    def get(self, request, pokemon_name):
        redis_pokemon = Pokemon.get(pokemon_name)
        if not redis_pokemon:
            return Response(
                data={"detail": "Pokemon not found"},
                status=404
            )
        redis_pokemon.translate_description()
        redis_pokemon.save()
        serializer = PokemonSerializer(data=redis_pokemon.serialize())
        if serializer.is_valid():
            return Response(
                data=serializer.data,
                status=200
            )
        return Response(
            data=serializer.errors,
            status=400
        )

        # return Response(
        #     data=serializer.data,
        #     status=200
        # )