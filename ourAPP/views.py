from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index_view(request):
    return render(request, 'index.html')


def home_view(request):
    return render(request, 'home.html')

def apropos_view(request):
    pass

def contacter_view(request):
    pass

def apropos_view(request):
    pass

def sinscrire_view(request):
    return render(request, 'registration.html')

def deconnecter_view(request):
    pass

