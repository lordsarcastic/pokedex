# pokedex
This service is a Pokedex in form of a REST API that returns Pokemon information

Task details can be accessed [here](https://docs.google.com/document/d/13EtWfHtIXEvMf-0HmbhsgX83EUlTUEdqPPIv4InbuuI/edit).

## Technologies used
- Server application:
    - [Django](https://www.djangoproject.com/), A Python web framework with focus on speed of development and perfectionism
    - [Django Rest Framework](https://www.django-rest-framework.org/), A sub-package for creating REST APIs with Django
    - [Redis](https://redis.io/), in-memory data store which can be used as a database, cache, streaming engine, and message broker.
    - [Postman](https://www.getpostman.com/), a complete API development environment, and flexibly integrates with the software development cycle for API testing.

## Installation
### Local installation
Running this service locally requires you to install Python and Redis. Install both of them by following the instructions in the link below:
 - Installation directions:
    - I used Python 3.9.10 as my Python version. You can get that exact version [here](https://www.python.org/downloads/release/python-3910/)
    - Redis can be installed by following the steps on the official website [here](https://redis.io/docs/getting-started/#install-redis)

- Basic installation:
    - Install [Python](https://www.python.org/) and [Redis](https://redis.io/) on your host environment (or PC).
    - Install [Pipenv](https://pipenv.pypa.io/en/latest/)  which is used to manage the virtual environment using `pip3 install pipenv`.
    - Ensure Git is installed, then clone this repository by running `git clone https://github.com/Lord-sarcastic/pokedex.git` in the terminal.
    - Enter the directory with `cd pokedex`
    - Create a `.env` file using the [.env.example](/.env.example) file as a template. Ensure to fill in appropriate values. The `DJANGO_ALLOWED_HOSTS` variable refers to the domain host you'll be running this app on.
    - Run `pipenv install` to install all necessary dependencies for the server application in a virtual environment.
    - Run `pipenv shell` to activate the virtual environment.
    - Run the server with `python manage.py runserver`. It should be running on port 5000.

### Docker
If you've got Docker installed, edit the `.docker.env` file to your taste (you wouldn't need to except you hate me), then run `docker-compose build` and `docker-compose up -d` to spin up the server.

The application should be running on port `5000` at URL: `localhost:5000`.

Note you're very likely to see this screen after running the `python manage.py runserver` command:
<img width="908" alt="Screenshot 2022-04-17 at 07 24 18" src="https://user-images.githubusercontent.com/33290249/163703305-c744debc-e645-4f67-ae57-a799e9cefa26.png">

This is because, Django expects us to use an actual database which should be plugged in via on of Django's interfaces. Migrations are usually run to create database tables but since we're making use of Redis, we don't need any of that. So, we can conveniently ignore the warnings.

## API Enpoints documentation
The application is made up of two routes which does the job of retrieving a Pokemon's detail, and a tranlation of a Pokemon's detail:

### The Pokemon detail endpoint
 `GET /pokemon/<pokemon_name>/` -> Retrieve a pokemon details in the form:
```json
{
    "name": "charmander",
    "description": "From the time it is born, a flame burns\nat the tip of its tail. Its life would end\nif the flame were to go out.",
    "habitat": "mountain",
    "isLegendary": false
}
```
If a pokemon does not exist, it returns:
```json
{
    "detail": "Pokemon not found"
}
```
with a status code of `404`
### The Pokemon translation endpoint
`GET /pokemon/translated/<pokemon_name>`:  Retrieve a Pokemon details whilst translating the description either to a Yoda form or a Shakespeare form. A typical response looks like so:
```json
{
    "name": "charmander",
    "description": "From the time 't is born,  a flame burns at the tip of its tail. Its life would end if 't be true the flame wast to wend out.",
    "habitat": "mountain",
    "isLegendary": false,
    "translation": "Yoda"
}
```

## Testing 🚨
Testing with Postman
- Install [Postman](https://www.getpostman.com/) or any preferred REST API Client such as [Insomnia](https://insomnia.rest/), [Rest Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client), etc.
- Get the application up and running by following the instructions in the Installation Guide of this README.

## Discussion
This section contains justifications and improvements that should be made.

### Why Django
Oh well, Django is a favourite framework of mine and while I could have used Flask or something else, it's quite easy to set up a Django application and structure your application in a way that it can actually scale in production, as long as structure is concerned.

### Choice of Database
I choose Redis for the purpose of caching requests. Since Pokemon information doesn't and rarely changes, once a user has requested for an info, it can as well be cached to reduce network calls subsequently. This improves speed of the application

### Improvements for a production API
- The translation API tends to return a 404 response when the rate limiting is activated. In production, it is better to proxy requests through a service that would modify server's fingerprint and enable more requests to be allowed. Or simply pay for premium service.

## Licence 🔐
[MIT licensed](/LICENSE) © [Ayodeji Adeoti](https://github.com/Lord-sarcatic)

## Credits 🙏
- Half of the Open Source Software community who contribute to the whole of the tools I use
- Guido Van Rossum, that pretty Python guy
- Others who would be thanked by my smiles and Quora tags
