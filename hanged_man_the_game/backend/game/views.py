
from django.http import HttpResponse
from .hangedMan import play, download_dictionary


def index(request, letter):
    print("You entered the letter: ", letter)
    res = "<h1>You entered the letter: </h1><h2><b>" + letter + "</b></h2>"
   # play()
    download_dictionary()
    return HttpResponse(res)
