from django.db import models
import pymongo
import nltk
nltk.download('stopwords')
default_stopwords = set(nltk.corpus.stopwords.words('spanish'))

def getNews(col_name):
    connection = pymongo.MongoClient("mongodb://localhost:27017")
    db = getattr(connection, col_name)
    news = db.noticiasFake.find()
    return list(news)

def getNewsGroupDate():
    connection = pymongo.MongoClient("mongodb://localhost:27017")
    db = connection.elPais
    news = db.noticiasFake.aggregate([
        {
            "$group": {
                "_id": {"fecha": "$fecha"},
                "count": {"$sum": 1},
                "fecha": {"$first": "$fecha"},
                "titulo": {"$push": '$titulo'}
            }
        },
        {
            "$sort": {"fecha": 1}
        }
    ])
    return list(news)

def getNewspapers():
    connection = pymongo.MongoClient("mongodb://localhost:27017")
    db = connection.periodicos
    newspapers = db.disponibles.find()
    return list(newspapers)

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
