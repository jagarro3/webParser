from django.urls import path

from . import views

app_name = 'newspapers'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('results.html', views.getResults, name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]

