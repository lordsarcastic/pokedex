from django.urls import include, path
from . import views


urlpatterns = [
    path('', include([
        path(
            'translated/<slug:pokemon_name>/',
            views.PokemonTranslateView.as_view(),
            name='pokemon-translate'
        ),
        path(
            '<slug:pokemon_name>/',
            views.PokemonRetrieveView.as_view(),
            name='pokemon-retrieve'
        ),
    ]))
]
