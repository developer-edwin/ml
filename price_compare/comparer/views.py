import re
import json
import datetime

from django.shortcuts import render
from django.utils import timezone
# from django.http import HttpResponse

# Create your views here.
# def index(request):
#     return HttpResponse("Hello world!")

from .models import Search

from .tools import scraping


def index(request):
    if "prompt" in request.POST and request.POST["prompt"]:
        saved_prompt = Search.objects.filter(prompt=request.POST["prompt"])
        if len(saved_prompt):
            if not saved_prompt[0].last_search >= timezone.now() - datetime.timedelta(hours=1):
                results = scraping(request.POST["prompt"])
                data_to_update = Search.objects.get(pk=saved_prompt[0].pk)
                data_to_update.last_search = timezone.now()
                data_to_update.data = json.dumps(results)
                data_to_update.save()
            else:
                if len(re.findall(r'mlstatic', saved_prompt[0].data)) > 10:
                    results = json.loads(saved_prompt[0].data)
                else:
                    results = scraping(request.POST["prompt"])
                    data_to_update = Search.objects.get(pk=saved_prompt[0].pk)
                    data_to_update.last_search = timezone.now()
                    data_to_update.data = json.dumps(results)
                    data_to_update.save()
        else:
            results = scraping(request.POST["prompt"])
            Search(prompt=request.POST["prompt"],last_search=timezone.now(), data=json.dumps(results)).save()
        results = scraping(request.POST["prompt"])
    else:
        results = []
    results_count = len(results)
    return render(request, 'comparer/index.html', {
        "results": results,
        "results_count": results_count,
    })
