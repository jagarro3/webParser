import itertools
import json
import os
import re
import time
import unicodedata
from collections import OrderedDict
from itertools import product
from multiprocessing import Pool, Value, cpu_count
from timeit import default_timer as timer

import matplotlib
import nltk
from bokeh.embed import components
from bokeh.plotting import figure, output_file, show
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse
from django.views import generic
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import ToktokTokenizer, sent_tokenize, word_tokenize
from wordcloud import WordCloud
from unidecode import unidecode
import unicodedata

from newspapers import models

# Stopworks
stop_wordsEN = stopwords.words('english')
stop_wordsES = stopwords.words('spanish')
newStopWordsES = ["0","1","2","3","4","5","6","7","8","9","_","a","actualmente","acuerdo","adelante","ademas","además","adrede","afirmó","agregó","ahi","ahora","ahí","al","algo","alguna","algunas","alguno","algunos","algún","alli","allí","alrededor","ambos","ampleamos","antano","antaño","ante","anterior","antes", "año", "años","apenas","aproximadamente","aquel","aquella","aquellas","aquello","aquellos","aqui","aquél","aquélla","aquéllas","aquéllos","aquí","arriba","arribaabajo","aseguró","asi","así","atras","aun","aunque","ayer","añadió","aún","b","bajo","bastante","bien","breve","buen","buena","buenas","bueno","buenos","c","cada","casi","cerca","cierta","ciertas","cierto","ciertos","cinco","claro","comentó","como","con","conmigo","conocer","conseguimos","conseguir","considera","consideró","consigo","consigue","consiguen","consigues","contigo","contra","cosas","creo","cual","cuales","cualquier","cuando","cuanta","cuantas","cuanto","cuantos","cuatro","cuenta","cuál","cuáles","cuándo","cuánta","cuántas","cuánto","cuántos","cómo","d","da","dado","dan","dar","de","debajo","debe","deben","debido","decir","dejó","del","delante","demasiado","demás","dentro","deprisa","desde","despacio","despues","después","detras","detrás","dia","dias","dice","dicen","dicho","dieron","diferente","diferentes","dijeron","dijo","dio","donde","dos","durante","día","días","dónde","e","ejemplo","el","ella","ellas","ello","ellos","embargo","empleais","emplean","emplear","empleas","empleo","en","encima","encuentra","enfrente","enseguida","entonces","entre","era","erais","eramos","eran","eras","eres","es","esa","esas","ese","eso","esos","esta","estaba","estabais","estaban","estabas","estad","estada","estadas","estado","estados","estais","estamos","estan","estando","estar","estaremos","estará","estarán","estarás","estaré","estaréis","estaría","estaríais","estaríamos","estarían","estarías","estas","este","estemos","esto","estos","estoy","estuve","estuviera","estuvierais","estuvieran","estuvieras","estuvieron","estuviese","estuvieseis","estuviesen","estuvieses","estuvimos","estuviste","estuvisteis","estuviéramos","estuviésemos","estuvo","está","estábamos","estáis","están","estás","esté","estéis","estén","estés","ex","excepto","existe","existen","explicó","expresó","f","fin","final","fue","fuera","fuerais","fueran","fueras","fueron","fuese","fueseis","fuesen","fueses","fui","fuimos","fuiste","fuisteis","fuéramos","fuésemos","g","general","gran","grandes","gueno","h","ha","haber","habia","habida","habidas","habido","habidos","habiendo","habla","hablan","habremos","habrá","habrán","habrás","habré","habréis","habría","habríais","habríamos","habrían","habrías","habéis","había","habíais","habíamos","habían","habías","hace","haceis","hacemos","hacen","hacer","hacerlo","haces","hacia","haciendo","hago","han","has","hasta","hay","haya","hayamos","hayan","hayas","hayáis","he","hecho","hemos","hicieron","hizo","horas","hoy","hube","hubiera","hubierais","hubieran","hubieras","hubieron","hubiese","hubieseis","hubiesen","hubieses","hubimos","hubiste","hubisteis","hubiéramos","hubiésemos","hubo","i","igual","incluso","indicó","informo","informó","intenta","intentais","intentamos","intentan","intentar","intentas","intento","ir","j","junto","k","l","la","lado","largo","las","le","lejos","les","llegó","lleva","llevar","lo","los","luego","lugar","m","mal","manera","manifestó","mas","mayor","me","mediante","medio","mejor","mencionó","menos","menudo","mi","mia","mias","mientras","mio","mios","mis","misma","mismas","mismo","mismos","modo","momento","mucha","muchas","mucho","muchos","muy","más","mí","mía","mías","mío","míos","n","nada","nadie","ni","ninguna","ningunas","ninguno","ningunos","ningún","no","nos","nosotras","nosotros","nuestra","nuestras","nuestro","nuestros","nueva","nuevas","nuevo","nuevos","nunca","o","ocho","os","otra","otras","otro","otros","p","pais","para","parece","parte","partir","pasada","pasado","paìs","peor","pero","pesar","poca","pocas","poco","pocos","podeis","podemos","poder","podria","podriais","podriamos","podrian","podrias","podrá","podrán","podría","podrían","poner","por","por qué","porque","posible","primer","primera","primero","primeros","principalmente","pronto","propia","propias","propio","propios","proximo","próximo","próximos","pudo","pueda","puede","pueden","puedo","pues","q","qeu","que","quedó","queremos","quien","quienes","quiere","quiza","quizas","quizá","quizás","quién","quiénes","qué","r","raras","realizado","realizar","realizó","repente","respecto","s","sabe","sabeis","sabemos","saben","saber","sabes","sal","salvo","se","sea","seamos","sean","seas","segun","segunda","segundo","según","seis","ser","sera","seremos","será","serán","serás","seré","seréis","sería","seríais","seríamos","serían","serías","seáis","señaló","si","sido","siempre","siendo","siete","sigue","siguiente","sin","sino","sobre","sois","sola","solamente","solas","solo","solos","somos","son","soy","soyos","su","supuesto","sus","suya","suyas","suyo","suyos","sé","sí","sólo","t","tal","tambien","también","tampoco","tan","tanto","tarde","te","temprano","tendremos","tendrá","tendrán","tendrás","tendré","tendréis","tendría","tendríais","tendríamos","tendrían","tendrías","tened","teneis","tenemos","tener","tenga","tengamos","tengan","tengas","tengo","tengáis","tenida","tenidas","tenido","tenidos","teniendo","tenéis","tenía","teníais","teníamos","tenían","tenías","tercera","ti","tiempo","tiene","tienen","tienes","toda","todas","todavia","todavía","todo","todos","total","trabaja","trabajais","trabajamos","trabajan","trabajar","trabajas","trabajo","tras","trata","través","tres","tu","tus","tuve","tuviera","tuvierais","tuvieran","tuvieras","tuvieron","tuviese","tuvieseis","tuviesen","tuvieses","tuvimos","tuviste","tuvisteis","tuviéramos","tuviésemos","tuvo","tuya","tuyas","tuyo","tuyos","tú","u","ultimo","un","una","unas","uno","unos","usa","usais","usamos","usan","usar","usas","uso","usted","ustedes","v","va","vais","valor","vamos","van","varias","varios","vaya","veces","ver","verdad","verdadera","verdadero","vez","vosotras","vosotros","voy","vuestra","vuestras","vuestro","vuestros","w","x","y","ya","yo","z","él","éramos","ésa","ésas","ése","ésos","ésta","éstas","éste","éstos","última","últimas","último","últimos"]
newStopWordsEN = ['june', 'reuters', 'a', 'about', 'above', 'across', 'after', 'again', 'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any', 'anybody', 'anyone', 'anything', 'anywhere', 'are', 'area', 'areas', 'around', 'as', 'ask', 'asked', 'asking', 'asks', 'at', 'away', 'b', 'back', 'backed', 'backing', 'backs', 'be', 'became', 'because', 'become', 'becomes', 'been', 'before', 'began', 'behind', 'being', 'beings', 'best', 'better', 'between', 'big', 'both', 'but', 'by', 'c', 'came', 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd', 'did', 'differ', 'different', 'differently', 'do', 'does', 'done', 'down', 'downed', 'downing', 'downs', 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'even', 'evenly', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact', 'facts', 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full', 'fully', 'further', 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'give', 'given', 'gives', 'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped', 'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself', 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in', 'interest', 'interested', 'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later', 'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm', 'made', 'make', 'making', 'man', 'many', 'may', 'me', 'member', 'members', 'men', 'might', 'more', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'necessary', 'need', 'needed', 'needing', 'needs', 'never', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nothing', 'now', 'nowhere', 'number', 'numbers', 'o', 'of', 'off', 'often', 'old', 'older', 'oldest', 'on', 'once', 'one', 'only', 'open', 'opened', 'opening', 'opens', 'or', 'order', 'ordered', 'ordering', 'orders', 'other', 'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps', 'place', 'places', 'point', 'pointed', 'pointing', 'points', 'possible', 'present', 'presented', 'presenting', 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather', 'really', 'right', 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'second', 'seconds', 'see', 'seem', 'seemed', 'seeming', 'seems', 'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows', 'side', 'sides', 'since', 'small', 'smaller', 'smallest', 'so', 'some', 'somebody', 'someone', 'something', 'somewhere', 'state', 'states', 'still', 'such', 'sure', 't', 'take', 'taken', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think', 'thinks', 'this', 'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today', 'together', 'too', 'took', 'toward', 'turn', 'turned', 'turning', 'turns', 'two', 'u', 'under', 'until', 'up', 'upon', 'us', 'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting', 'wants', 'was', 'way', 'ways', 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where', 'whether', 'which', 'while', 'who', 'whole', 'whose', 'why', 'will', 'with', 'within', 'without', 'work', 'worked', 'working', 'works', 'would', 'x', 'y', 'year', 'years', 'yet', 'you', 'young', 'younger', 'youngest', 'your', 'yours', 'z']
stop_wordsES.extend(newStopWordsES)
stop_wordsEN.extend(newStopWordsEN)
toktok = ToktokTokenizer()
global selectNewspaper
global fromDate
global toDate
global categories

class IndexView(generic.ListView):
    template_name = 'newspapers/index.html'
    context_object_name = 'newspapers'

    def get_queryset(self):
        newspapers = models.getNewspapers()
        return newspapers

class ResultsView(generic.DetailView):
    template_name = 'newspapers/results.html'

def getResults(request):
    start = timer()

    template = loader.get_template('newspapers/results.html')
    
    # Obtener datos index.html
    selectNewspaper = request.POST['selectOfNewspapers']
    fromDate = request.POST['daterange'].split('-')[0]
    toDate = request.POST['daterange'].split('-')[1]
    categories = [category.strip() for category in request.POST['categories'].split(',')]
    wordsSearch = [word.strip() for word in request.POST['wordsSearch'].split(',')]
    optAndOr = request.POST['optAndOr']
    
    # Obtener idioma del periodico
    start_time = time.time()
    language = models.getLenguageOfNewspaper(selectNewspaper)[0]['idioma']
    print("--- %s getLenguageOfNewspaper ---" % (time.time() - start_time))

    # Lista de articulos con el texto en bruto
    start_time = time.time()
    articlesRaw = getArticlesRawV2(fromDate, toDate, categories, wordsSearch, optAndOr, selectNewspaper)
    print("--- %s getArticlesRawV2 ---" % (time.time() - start_time))

    # Limpiar la noticia y añadirla a cada element del diccionario
    start_time = time.time()
    for article in articlesRaw:
        article['noticiaProcesada'] = cleanArticleV2(article['noticia'], language)
    print("--- %s cleanArticleV2 ---" % (time.time() - start_time))

    # Obtener información básica de los datos
    start_time = time.time()
    numWordsText, numWordsTextCleaned, numWordsTitle, countArticles = getRawInfoOfData(articlesRaw)
    numWordsRemoved = numWordsText - numWordsTextCleaned
    print("--- %s getRawInfoOfData ---" % (time.time() - start_time))

    # Gráficas de wordCloud
    start_time = time.time()
    imageWordCloud = getWordCloud(articlesRaw)
    print("--- %s getWordCloud ---" % (time.time() - start_time))

    start_time = time.time()
    imageWordCloudBigrams = getWordCloudBigrams(articlesRaw)
    print("--- %s getWordCloudBigrams ---" % (time.time() - start_time))

    # Gráfica de barras
    start_time = time.time()
    scriptFrequency, divFrequency = graphFrequency(articlesRaw)
    print("--- %s graphFrequency ---" % (time.time() - start_time))

    # Gráfica con la palabra mas frecuente en cada fecha
    start_time = time.time()
    diccDateArticles = orderByMonthYear(articlesRaw, 'noticiaProcesada', language)
    print("--- %s orderByMonthYear ---" % (time.time() - start_time))

    start_time = time.time()
    mostFrequenceWordPerDay = frequencyWordsByDate(diccDateArticles)
    print("--- %s frequencyWordsByDate ---" % (time.time() - start_time))

    start_time = time.time()
    mostFrequenceBigramPerDay = frequencyBigramsByDate(diccDateArticles)
    print("--- %s frequencyBigramsByDate ---" % (time.time() - start_time))

    end = timer()
    timeProcess = end - start

    context = {
        'nombrePeriodico': selectNewspaper,
        'rangoDesde': fromDate,
        'rangoHasta': toDate,
        'palabrasFiltradas': ', '.join(wordsSearch),
        'categoriasFiltradas': ', '.join(categories),
        'numeroPalabrasNoticia': numWordsText,
        'numeroPalabrasNoticiaProcesada': numWordsTextCleaned,
        'numeroPalabrasTitulo': numWordsTitle,
        'numeroNoticias': countArticles,
        'numeroPalabrasEliminadas': numWordsRemoved,
        'imagenWordCloud': imageWordCloud,
        'imagenWordCloudBigrams': imageWordCloudBigrams,
        'divFrequency': divFrequency,
        'scriptFrequency': scriptFrequency,
        'mostFrequenceWordPerDay': mostFrequenceWordPerDay,
        'mostFrequenceBigramPerDay': mostFrequenceBigramPerDay,
        'articlesRaw': articlesRaw,
        'timeProcess': timeProcess
    }
    
    return HttpResponse(template.render(context, request))

# Obtener las noticias sin limpiar
def getArticlesRaw(fromDate, toDate, categories, selectNewspaper):
    articles = models.getNewsByRangeDate(fromDate, toDate, selectNewspaper)
    articlesFiltered = []
    
    for article in articles:
        tags = ','.join(article['tags'])

        if all(unicodedata.normalize('NFKD', word.lower()).encode('ASCII', 'ignore').decode() 
        in unicodedata.normalize('NFKD', tags.lower()).encode('ASCII', 'ignore').decode() 
        for word in categories):
            articlesFiltered.append(article)

    return articlesFiltered

def getArticlesRawV2(fromDate, toDate, categories, wordsSearch, optAndOr, selectNewspaper):
    articles = models.getNewsByRangeDate(fromDate, toDate, selectNewspaper)
    articlesFiltered = []

    # Si no hay filtros aplicados
    if(len(categories) == 1 and categories[0] == "" and len(wordsSearch) == 1 and wordsSearch[0] == ""):
        return articles

    # Si hay categorias pero no noticias
    if(len(categories) > 0 and categories[0] != "" and len(wordsSearch) == 1 and wordsSearch[0] == ""):
        for article in articles:
            tags = [tag.lower() for tag in article['tags']]
            if all(word.lower() in tags for word in categories):
                articlesFiltered.append(article)
        return articlesFiltered

    # Si hay noticias pero no caterogorias
    if(len(categories) == 1 and categories[0] == "" and len(wordsSearch) > 0 and wordsSearch[0] != ""):
        for article in articles:
            if all(True if article['noticia'].lower().find(word.lower()) > -1 else False for word in wordsSearch):
                articlesFiltered.append(article)
        return articlesFiltered

    # Si están aplicados ambos filtros, entonces entra en juego el operador lógico And y Or
    for article in articles:
        tags = [tag.lower() for tag in article['tags']]
        if optAndOr == "and":
            if all(True if article['noticia'].lower().find(word.lower()) > -1 else False for word in wordsSearch):
                if all(word.lower() in tags for word in categories):
                    articlesFiltered.append(article)           
        else:
            if (all(True if article['noticia'].lower().find(word.lower()) > -1 else False for word in wordsSearch) and len(wordsSearch) > 0) or (all(word.lower() in tags for word in categories) and len(categories) > 0):
                articlesFiltered.append(article)

    return articlesFiltered

# Obtener datos en crudo
def getRawInfoOfData(articles):
    countWordsText, countWordsTextCleaned, countWordsTitle, countArticles  = 0, 0, 0, 0

    for x in articles:
        countWordsText += len(x['noticia'].split())
        countWordsTextCleaned += len(x['noticiaProcesada'])
        countWordsTitle += len(x['titulo'].split())
        countArticles += 1

    return countWordsText, countWordsTextCleaned, countWordsTitle, countArticles

# Obtener imagen WordCloud
def getWordCloud(articles):
    print(len(articles))
    if len(articles) > 0:
        print("ENTRA")
        articles = [item for article in articles for item in article['noticiaProcesada']]  
        fdist = FreqDist(articles)
        wordcloud = WordCloud(background_color="white", max_words=50).fit_words(fdist)
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "./static/img/wordcloud.jpg")
        wordcloud.to_file(path)
        return ('wordcloud.jpg')

def getWordCloudBigrams(articles):
    if len(articles) > 0:
        bigrams = []
        for article in articles:
            bigrams.append(list(nltk.bigrams(article['noticiaProcesada'])))

        bigrams = [item for sublist in bigrams for item in sublist]  
        bigrams = [" ".join(tup) for tup in bigrams]
    
        fdist = FreqDist(bigrams)

        wordcloud = WordCloud(background_color="white", max_words=50).fit_words(fdist)

        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "./static/img/wordcloudBigrams.jpg")
        wordcloud.to_file(path)

        return ('wordcloudBigrams.jpg')

# Obtener grafico de barras con las palabras mas frecuentes
def graphFrequency(articles):
    articles = [item for article in articles for item in article['noticiaProcesada']]  
    fdist = FreqDist(articles)
    most_common = fdist.most_common(5)

    words = [word for word, value in most_common]
    counts = [value for word, value in most_common]
    p = figure(x_range=words, plot_height=300)

    p.vbar(x=words, top=counts, width=0.9)

    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    #Store components 
    scriptFrequency, graphFrequency = components(p)
    return scriptFrequency, graphFrequency

# Diccionario con noticias por fecha
def orderByMonthYear(listN, field, language):
    dicc = {}

    for elem in listN:
        if elem['fecha'].strftime("%d-%m-%Y") in dicc:
            dicc[elem['fecha'].strftime("%d-%m-%Y")] += elem[field]
        else:
            dicc[elem['fecha'].strftime("%d-%m-%Y")] = elem[field]
    
    return dicc

# Obtener tabla con la palabra mas frecuente de cada día
def frequencyWordsByDate(dicc):
    diccPerDay = {}
    for key, val in dicc.items():
        fdist = FreqDist(val)
        if len(fdist.most_common(1)) > 0:
            word, count = fdist.most_common(1)[0]
            diccPerDay[key] = word + ' (' +  str(count) + ')'
    
    return diccPerDay

# Obtener tabla con el bigrama mas frecuente de cada día
def frequencyBigramsByDate(dicc):
    diccPerDay = {}
    for key, val in dicc.items():
        bigrams = []
        bigrams.append(list(nltk.bigrams(val)))
        bigrams = [item for sublist in bigrams for item in sublist]  
        bigrams = [" ".join(tup) for tup in bigrams]
        fdist = FreqDist(bigrams)
        if len(fdist.most_common(1)) > 0:
            word, count = fdist.most_common(1)[0]
            diccPerDay[key] = word + ' (' +  str(count) + ')'
    return diccPerDay

# Limpiar el texto de una sola noticia
def cleanArticle(article, language):

    tokens, wordsStopWords = [], []
    
    # Tokenizar
    tokens = toktok.tokenize(article)

    # Minusculas y no numerico/signos
    wordsUnsigned = [word.lower() for word in tokens if word.isalpha()]   

    # Stopworks
    if language == 'ingles':
        wordsStopWords = [word for word in wordsUnsigned if word not in stop_wordsEN]
    else:
        wordsStopWords = [word for word in wordsUnsigned if word not in stop_wordsES]
      
    return wordsStopWords

# Limpiar el texto de una sola noticia de forma más efectiva
def cleanArticleV2(article, language):
    tokens, wordsStopWords = [], []

    article = article.replace('ñ', 'ny')
    no_accents = unicodedata.normalize('NFD', article.lower()).encode('ascii', 'ignore').decode("utf-8")

    result = re.sub('[^A-Za-z]+', ' ', no_accents)
    result = re.sub(r'\b\w{1,2}\b', '', result)
  
    # Tokenizar
    tokens = toktok.tokenize(result)

    # # Stopworks
    if language == 'ingles':
        wordsStopWords = [word for word in tokens if word not in stop_wordsEN]
    else:
        wordsStopWords = [word for word in tokens if word not in stop_wordsES]
    return wordsStopWords