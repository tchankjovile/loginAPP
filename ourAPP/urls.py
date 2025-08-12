from django.urls import path
from .views import *

urlpatterns=[
    path('' , index_view, name= "index"),
    path('home/', home_view, name= "home_name"),
    path('contact/', contacter_view, name= "contacter_name"),
    path('apropos/', apropos_view, name= "apropos_name"),
    path('sinscrire/', sinscrire_view, name= "sinscrire_name"),
    path('deconnecter/', deconnecter_view, name= "deconnecter_name"),
]