from datetime import timezone
from enum import unique
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
import re


# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password= None, **extra_fields):
        if not username:
            raise ValueError(' le champ "nom d\'utilisateur " doit être renseigné')
        if not extra_fields.get("is_superuser", False):
            if not username.lower().endswith('@gmail.com'):
                raise ValueError('vous devez définir votre adresse mail comme nom d\'utilisateur')
        user= self.model(username= username, **extra_fields)
        user.set_password(password)
        user.save(using= self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("le super utilisateur doit avoir is_staff= True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('le superutilisateur doit avoir is_superuser= True')

        if not password:# le mot de passe est obligatoire pour l'administrateur
            raise ValueError("Un mot de passe est obligatoire pour un superutilisateur.")

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES= (
        ('admin', 'administrateur'),
         ('partenaire', 'partenaire'),
        ('candidat', 'candidat'),
    )
    username= models.CharField(max_length= 150, unique= True)
    is_active = models.BooleanField(default= True)
    is_staff= models.BooleanField(default= False)

    user_type= models.CharField(max_length= 15, choices= USER_TYPE_CHOICES)

    def is_partenaire(self):
        return self.user_type== 'partenaire'

    def is_candidat(self):
        return self.user_type== 'candidat'

    def is_admin(self):
        return self.user_type== 'admin'

    USERNAME_FIELD= 'username'# faudra configurer le susername si comme étant l'adresse mail de l'utilisateur, comme ça un mail pourra lui être envoyé concernant son password
    REQUIRED_FIELDS = []
    objects= CustomUserManager()



class Partenaire(models.Model):
    user= models.OneToOneField(User, on_delete= models.CASCADE)
    nom= models.CharField(max_length= 150)
    nom_du_centre= models.CharField(max_length=150)
    # email= models.EmailField(null= True, blank=True)
    numero_telephone= PhoneNumberField(unique= True, null= False, blank= False)

    def __str__(self):
        return f"{self.nom} {self.nom_du_centre}"


class Candidat(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nom= models.CharField(max_length=150)
    prenom= models.CharField(max_length=150)
    email= models.EmailField(null= True, blank= True)# représente l'adresse mail que l'administrateur va créér lui même
    nationnalite= models.CharField(max_length=150, null= True, blank= True)
    profession= models.CharField(max_length=150, null= True, blank= True)
    date_naissance= models.DateField(null= True, blank= True)
    lieu_naissance= models.CharField(max_length=150, null= True, blank= True)
    numero_telephone= PhoneNumberField(unique= True)
    photo_portrait= models.ImageField(upload_to='media/portrait/', help_text= "L'image doit être clair, de préférence avec fond blanc", max_length= 300)
    piece_identite_recto= models.ImageField(upload_to='media/piecesidentite/', help_text="La piece fdoit être à jour et les informations doivent être lisibles", max_length= 300)
    piece_identite_verso= models.ImageField(upload_to='media/piecesidentite/', help_text="La piece fdoit être à jour et les informations doivent être lisibles", max_length= 300, default=None)
    confirmation = models.ImageField(upload_to= 'media/confirmation/', null=True, blank= True)#la photo de confirmation que nous enverons si il est inscrit
    ville_residence= models.CharField(max_length= 150)
    langue_usuelle= models.CharField(max_length= 150)
    budget= models.IntegerField(null=True, blank= True, default= 0)#le montant qui a été arrêté
    favoris= models.BooleanField(default= False, null= True, blank= True)# permettant de mettre le condidat en tete de file
    statuts_choices= (
        ("En Attente", "En Attente"),# quand il vient de créer son profile
        ("Approuvé", "Approuvé"),# quand son profile a été vérifier par l'administrateur et à été validé
        ("Validé", "Validé"),#quand il a été bel et bien inscrit
        ("Non Validé", "Non Validé"),# quand son inscription a réussi
    )
    statut= models.CharField(max_length=20, choices= statuts_choices, default= "En Attente")
    partenaire = models.ForeignKey(Partenaire, on_delete= models.SET_NULL, null=True, blank= True, verbose_name= "related partenaire")

    def get_absolute_url(self):
        return reverse('description', kwargs={"id": str(self.id)})

    def get_modify_url(self):
        return reverse('modifycandidat_name', kwargs={"id": str(self.id)})

    def get_delete_url(self):
        return reverse('delete', kwargs={"id": str(self.id)})


    def __str__(self):
        return f"{self.nom}"


class Collaborateur(models.Model):
    nom = models.CharField(max_length= 100)
    score= models.IntegerField()
    telephone= PhoneNumberField( unique= True, null= False, blank= False)
    def __str__(self):
        return f"{self.nom} {self.score}"

class Notification(models.Model):
    libelle= models.TextField()
    user= models.ForeignKey(User, on_delete= models.CASCADE, null= True, blank= True)
    date= models.DateTimeField(default= timezone.now)

