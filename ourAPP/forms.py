from django import forms

from ourAPP.models import Candidat


class ModifyCandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields=('nom', 'prenom', 'numero_telephone', 'langue_usuelle', 'budget', 'ville_residence', 'photo_portrait', 'piece_identite_recto', 'piece_identite_verso')
