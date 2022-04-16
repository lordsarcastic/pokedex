from rest_framework import serializers


class PokemonSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    habitat = serializers.CharField(default=None)
    isLegendary = serializers.BooleanField()
