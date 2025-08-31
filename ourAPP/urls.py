from django.urls import path
from .views import *
from django.contrib.auth import views  as auth_views

urlpatterns=[
    path('' , index_view, name= "index"),
path('login/', login_view, name='login'),
    path('homeC/', homecandidat_view, name= "homecandidat_name"),
    path('homeP/', homepartenaire_view, name= "homepartenaire_name"),
    path('adjoutcandidat/', ajoutcandidat_view, name= "ajoutcandidat_name"),
    path('detailcandidat/<int:candidat_id>/', detailcandidat_view, name= "detailcandidat_name"),
    path('candidat/<int:candidat_id>/change-favoris/', change_favoris_view, name= "changefavoris_name"),
    path('contact/', contacter_view, name= "contacter_name"),
    path('apropos/', apropos_view, name= "apropos_name"),
    path('sinscrire/', sinscrire_view, name= "sinscrire_name"),
    path('sinscrire2/', sinscrire_view2, name= "sinscrire2"),
    path('sinscrire3/', sinscrire_view3, name= "sinscrire3"),
    path('modify_candidat/', modifycandidat_view, name= "modifycandidat_name"),
    path('confirm_candidat/', confirmcandidat_view, name= "confirmcandidat_name"),
    path('logout/', logout_view, name="logout"),
]