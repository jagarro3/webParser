from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.template import loader
import json
import itertools
from multiprocessing import Pool, Value, cpu_count
from itertools import product
from .models import Choice, Question
from newspapers import models
import re
import nltk
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize, ToktokTokenizer
import time

# Stopworks
stop_wordsEN = stopwords.words('english')
stop_wordsES = stopwords.words('spanish')
newStopWordsES = ["0","1","2","3","4","5","6","7","8","9","_","a","actualmente","acuerdo","adelante","ademas","además","adrede","afirmó","agregó","ahi","ahora","ahí","al","algo","alguna","algunas","alguno","algunos","algún","alli","allí","alrededor","ambos","ampleamos","antano","antaño","ante","anterior","antes","apenas","aproximadamente","aquel","aquella","aquellas","aquello","aquellos","aqui","aquél","aquélla","aquéllas","aquéllos","aquí","arriba","arribaabajo","aseguró","asi","así","atras","aun","aunque","ayer","añadió","aún","b","bajo","bastante","bien","breve","buen","buena","buenas","bueno","buenos","c","cada","casi","cerca","cierta","ciertas","cierto","ciertos","cinco","claro","comentó","como","con","conmigo","conocer","conseguimos","conseguir","considera","consideró","consigo","consigue","consiguen","consigues","contigo","contra","cosas","creo","cual","cuales","cualquier","cuando","cuanta","cuantas","cuanto","cuantos","cuatro","cuenta","cuál","cuáles","cuándo","cuánta","cuántas","cuánto","cuántos","cómo","d","da","dado","dan","dar","de","debajo","debe","deben","debido","decir","dejó","del","delante","demasiado","demás","dentro","deprisa","desde","despacio","despues","después","detras","detrás","dia","dias","dice","dicen","dicho","dieron","diferente","diferentes","dijeron","dijo","dio","donde","dos","durante","día","días","dónde","e","ejemplo","el","ella","ellas","ello","ellos","embargo","empleais","emplean","emplear","empleas","empleo","en","encima","encuentra","enfrente","enseguida","entonces","entre","era","erais","eramos","eran","eras","eres","es","esa","esas","ese","eso","esos","esta","estaba","estabais","estaban","estabas","estad","estada","estadas","estado","estados","estais","estamos","estan","estando","estar","estaremos","estará","estarán","estarás","estaré","estaréis","estaría","estaríais","estaríamos","estarían","estarías","estas","este","estemos","esto","estos","estoy","estuve","estuviera","estuvierais","estuvieran","estuvieras","estuvieron","estuviese","estuvieseis","estuviesen","estuvieses","estuvimos","estuviste","estuvisteis","estuviéramos","estuviésemos","estuvo","está","estábamos","estáis","están","estás","esté","estéis","estén","estés","ex","excepto","existe","existen","explicó","expresó","f","fin","final","fue","fuera","fuerais","fueran","fueras","fueron","fuese","fueseis","fuesen","fueses","fui","fuimos","fuiste","fuisteis","fuéramos","fuésemos","g","general","gran","grandes","gueno","h","ha","haber","habia","habida","habidas","habido","habidos","habiendo","habla","hablan","habremos","habrá","habrán","habrás","habré","habréis","habría","habríais","habríamos","habrían","habrías","habéis","había","habíais","habíamos","habían","habías","hace","haceis","hacemos","hacen","hacer","hacerlo","haces","hacia","haciendo","hago","han","has","hasta","hay","haya","hayamos","hayan","hayas","hayáis","he","hecho","hemos","hicieron","hizo","horas","hoy","hube","hubiera","hubierais","hubieran","hubieras","hubieron","hubiese","hubieseis","hubiesen","hubieses","hubimos","hubiste","hubisteis","hubiéramos","hubiésemos","hubo","i","igual","incluso","indicó","informo","informó","intenta","intentais","intentamos","intentan","intentar","intentas","intento","ir","j","junto","k","l","la","lado","largo","las","le","lejos","les","llegó","lleva","llevar","lo","los","luego","lugar","m","mal","manera","manifestó","mas","mayor","me","mediante","medio","mejor","mencionó","menos","menudo","mi","mia","mias","mientras","mio","mios","mis","misma","mismas","mismo","mismos","modo","momento","mucha","muchas","mucho","muchos","muy","más","mí","mía","mías","mío","míos","n","nada","nadie","ni","ninguna","ningunas","ninguno","ningunos","ningún","no","nos","nosotras","nosotros","nuestra","nuestras","nuestro","nuestros","nueva","nuevas","nuevo","nuevos","nunca","o","ocho","os","otra","otras","otro","otros","p","pais","para","parece","parte","partir","pasada","pasado","paìs","peor","pero","pesar","poca","pocas","poco","pocos","podeis","podemos","poder","podria","podriais","podriamos","podrian","podrias","podrá","podrán","podría","podrían","poner","por","por qué","porque","posible","primer","primera","primero","primeros","principalmente","pronto","propia","propias","propio","propios","proximo","próximo","próximos","pudo","pueda","puede","pueden","puedo","pues","q","qeu","que","quedó","queremos","quien","quienes","quiere","quiza","quizas","quizá","quizás","quién","quiénes","qué","r","raras","realizado","realizar","realizó","repente","respecto","s","sabe","sabeis","sabemos","saben","saber","sabes","sal","salvo","se","sea","seamos","sean","seas","segun","segunda","segundo","según","seis","ser","sera","seremos","será","serán","serás","seré","seréis","sería","seríais","seríamos","serían","serías","seáis","señaló","si","sido","siempre","siendo","siete","sigue","siguiente","sin","sino","sobre","sois","sola","solamente","solas","solo","solos","somos","son","soy","soyos","su","supuesto","sus","suya","suyas","suyo","suyos","sé","sí","sólo","t","tal","tambien","también","tampoco","tan","tanto","tarde","te","temprano","tendremos","tendrá","tendrán","tendrás","tendré","tendréis","tendría","tendríais","tendríamos","tendrían","tendrías","tened","teneis","tenemos","tener","tenga","tengamos","tengan","tengas","tengo","tengáis","tenida","tenidas","tenido","tenidos","teniendo","tenéis","tenía","teníais","teníamos","tenían","tenías","tercera","ti","tiempo","tiene","tienen","tienes","toda","todas","todavia","todavía","todo","todos","total","trabaja","trabajais","trabajamos","trabajan","trabajar","trabajas","trabajo","tras","trata","través","tres","tu","tus","tuve","tuviera","tuvierais","tuvieran","tuvieras","tuvieron","tuviese","tuvieseis","tuviesen","tuvieses","tuvimos","tuviste","tuvisteis","tuviéramos","tuviésemos","tuvo","tuya","tuyas","tuyo","tuyos","tú","u","ultimo","un","una","unas","uno","unos","usa","usais","usamos","usan","usar","usas","uso","usted","ustedes","v","va","vais","valor","vamos","van","varias","varios","vaya","veces","ver","verdad","verdadera","verdadero","vez","vosotras","vosotros","voy","vuestra","vuestras","vuestro","vuestros","w","x","y","ya","yo","z","él","éramos","ésa","ésas","ése","ésos","ésta","éstas","éste","éstos","última","últimas","último","últimos"]
stop_wordsES.extend(newStopWordsES)

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
    # context = {'periodicoSeleccionado': selectNewspaper}
    # getStatistics(selectNewspaper)
    context = {'periodicoSeleccionado':  getStatistics(selectNewspaper)}
    return HttpResponse(template.render(context, request))


def getStatistics(newspaperSelected):
    news = models.getNews(newspaperSelected)
    language = models.getLenguageOfNewspaper(newspaperSelected)[0]['idioma']

    listSorted = orderByMonthYear(news, 'noticia')

    listCommon = []


    start_time = time.time()
    
    for k, v in listSorted.items():
        listCommon.append({k: FreqDist(cleanText(v, language)).most_common(3)})

    elapsed_time = time.time() - start_time
    print('Tiempo ejecución:', elapsed_time, 'segundos')
    
    return listCommon

def orderByMonthYear(listN, field):
    dicc = {}
    for elem in listN:
        if elem['fecha'].strftime("%Y-%m") in dicc:
            dicc[elem['fecha'].strftime("%Y-%m")] += [elem[field]]
        else:
            dicc[elem['fecha'].strftime("%Y-%m")] = [elem[field]]
    return dicc



toktok = ToktokTokenizer()
from functools import reduce

def cleanText(articles, language):
    # Tokenizar
    for x in articles:
        tokens = [toktok.tokenize(y) for y in sent_tokenize(x)]
    # Flat list   
    tokens = [item for sublist in tokens for item in sublist]    
    # Minusculas
    word = [word.lower() for word in tokens]
    # Quitar numeros y signos
    wordsUnsigned = [word for word in word if word.isalpha()]
    # Stopworks
    if language == 'ingles':
        wordsStopWords = [word for word in wordsUnsigned if word not in stop_wordsEN]
    else:
        wordsStopWords = [word for word in wordsUnsigned if word not in stop_wordsES]

    return wordsStopWords

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
