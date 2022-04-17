from rest_framework import serializers


class PokemonSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    isLegendary = serializers.BooleanField()
    habitat = serializers.CharField(default=None, allow_null=True, read_only=True)

class PokemonTranslatedSerializer(PokemonSerializer):
    translation = serializers.CharField()
