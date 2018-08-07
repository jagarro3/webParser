from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.template import loader

from .models import Choice, Question, getNews, getNewsGroupDate, getNewspapers
from newspapers import models

import nltk
from nltk import FreqDist
from nltk.corpus import stopwords
stopwords = set(stopwords.words('spanish'))

global selectNewspaper


class IndexView(generic.ListView):
    template_name = 'newspapers/index.html'
    context_object_name = 'newspapers'

    def get_queryset(self):
        newspapers = models.getNewspapers()
        return newspapers


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'newspapers/results.html'


def getResults(request):
    template = loader.get_template('newspapers/results.html')
    selectNewspaper = request.POST['selectOfNewspapers']
    context = {'periodicoSeleccionado': selectNewspaper}
    getStatistics(selectNewspaper)
    return HttpResponse(template.render(context, request))


def getStatistics(col_name):
    news = models.getNews(col_name)
    titles = []
    for x in news:
        titles.append(x["titulo"])
    words = " ".join(titles).split()
    words = [w for w in words if w.lower() not in stopwords]
    fdist1 = FreqDist(words)
    print(fdist1.most_common(10))
    return news

# class IndexView(generic.ListView):
#     template_name = 'newspapers/index.html'
#     context_object_name = 'noticias'

#     def get_queryset(self):
#         news = models.getNews()
#         titles = []
#         for x in news:
#             titles.append(x["titulo"])
#         words = " ".join(titles).split()
#         words = [w for w in words if w.lower() not in stopwords]
#         fdist1 = FreqDist(words)
#         print(fdist1.most_common(10))
#         return news

# def get_queryset(self):
#     news = models.getNewsGroupDate()
#     for titles in news:
#         words = " ".join(titles["titulo"]).split()
#         # sentence = ' '.join(str(x) for x in titles["titulo"])
#         words = ' '.join(w for w in words if w.lower() not in stopwords)
#         fdist1 = FreqDist(words.split())
#     return news


class DetailView(generic.DetailView):
    model = Question
    template_name = 'newspapers/detail.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'newspapers/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('newspapers:results', args=(question.id,)))
