from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.shortcuts import render

# Create your views here.
from django.template.response import TemplateResponse

from racebets.scraper import get_results


def index(request):
    template = loader.get_template('index.html')

    return TemplateResponse(request, template, {'message': False})


def bet_results(request):
    if request.method == 'POST':
        racedata = request.POST.dict()
        results = get_results(racedata['date'].replace('-', '/'), racedata['race'])
        print(results)
        if results == 'dateError':
            message = 'No races found on ' + racedata['date'] + '.'
            messages.error(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        elif results == 'raceError':
            message = 'Race no. ' + racedata['race'] + ' does not exist on ' + racedata['date'] + '.'
            messages.error(request, message)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            template = loader.get_template('bet-results.html')
            return TemplateResponse(request, template, {'bet_res': results[0], 'dividends': results[1], 'bets': results[2], 'netpl': results[3], 'date': racedata['date'], 'race': racedata['race']})