from django.contrib import admin

from ourAPP.models import *

# Register your models here.

admin.site.register(User)
admin.site.register(Partenaire)
admin.site.register(Candidat)
admin.site.register(Collaborateur)
admin.site.register(Notification)