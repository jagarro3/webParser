from datetime import datetime

import nltk
import pymongo
from django.db import models


def getNews(col_name):
    connection = pymongo.MongoClient("mongodb://localhost:27017")
    db = connection.periodicos
    news = db[col_name].find().sort("fecha", pymongo.ASCENDING)
    return list(news)

def getNewsGroupDate(col_name):
    connection = pymongo.MongoClient("mongodb://localhost:27017")
    db = connection.periodicos
    news = db[col_name].aggregate([
        {
            "$group": {
                "_id": {"$month": "$fecha"},
                "count": {"$sum": 1},
                "fecha": {"$first": "$fecha"},
                "noticia": {"$push": '$titulo'}
            }
        }
    ])
    return list(news)

def getLenguageOfNewspaper(name):
    connection = pymongo.MongoClient("mongodb://localhost:27017")
    db = connection.periodicos
    return list(db.disponibles.find({'value': name}))

def getNewspapers():
    connection = pymongo.MongoClient("mongodb://localhost:27017")
    db = connection.periodicos
    newspapers = db.disponibles.find()
    return list(newspapers)

def getNewsByRangeDate(fromDate, toDate, col_name):
    # Convertir string en Datetime
    start = datetime.strptime(fromDate.strip(), '%m/%d/%Y')
    end = datetime.strptime(toDate.strip(), '%m/%d/%Y')

    # Consulta filtrada por fecha
    connection = pymongo.MongoClient("mongodb://localhost:27017")
    db = connection.periodicos
    newspapers = db[col_name].find({'fecha': {'$lt': end, '$gt': start}})
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
