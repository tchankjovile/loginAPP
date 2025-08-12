from enum import unique

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password= None, **extra_fields):
        if not username:
            raise ValueError(' le champ "username" doit être renseigné')
        user= self.model(username= username, **extra_fields)
        user.set_password(password)
        user.save(using= self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("le super utilisateur doit avoir is_staff= True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('le superutilisateur doit avoir is_superuser= True')

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES= (
        ('admin', 'administrateur'),
         ('partenaire', 'partenaire'),
        ('candidat', 'candidat'),
    )
    username= models.CharField(max_length=150, unique = True)
    is_active = models.BooleanField(default= True)
    is_staff= models.BooleanField(default= False)

    user_type= models.CharField(max_length= 15, choices= USER_TYPE_CHOICES)

    def is_Partenaire(self):
        return self.user_type== 'partenaire'

    def is_candidat(self):
        return self.user_type== 'candidat'

    def is_admin(self):
        return self.user_type== 'admin'

    USERNAME_FIELD= 'username'
    REQUIRED_FIELDS = []
    objects= CustomUserManager()



class Partenaire(models.Model):
    user= models.OneToOneField(User, on_delete= models.CASCADE)
    nom= models.CharField(max_length= 150)
    nom_du_centre= models.CharField(max_length=150)
    numero_telephone= PhoneNumberField(unique= True, null= False, blank= False)

    def __str__(self):
        return f"{self.nom} {self.nom_du_centre}"


class Candidat(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nom= models.CharField(max_length=150)
    prenom= models.CharField(max_length=150)
    email= models.EmailField()
    nationnalite= models.CharField(max_length=150)
    profession= models.CharField(max_length=150)
    date_naissance= models.DateField()
    lieu_naissance= models.CharField(max_length=150)
    telephone= PhoneNumberField(unique= True)
    photo_portrait= models.ImageField(upload_to='photo/portrait/', help_text= "L'image doit être clair, de préférence avec fond blanc")
    piece_identite_recto= models.ImageField(upload_to='photo/piecesidentite/', help_text="La piece fdoit être à jour et les informations doivent être lisibles")
    piece_identite_verso= models.ImageField(upload_to='photo/piecesidentite/', help_text="La piece fdoit être à jour et les informations doivent être lisibles", default= None)
    confirmation = models.ImageField(upload_to= 'photo/confirmation/')#la photo de confirmation que nous enverons si il est inscrit
    ville_residence= models.CharField(max_length= 150)
    langue_usuelle= models.CharField(max_length= 150)
    budget= models.IntegerField(null=True, blank= True, default= 0)#le montant qui a été arrêté
    favoris= models.BooleanField(default= False)# permettant de mettre le condidat en tete de file
    statuts_choices= (
        ("EA", "En Attente"),
        ("A", "Approuvé"),
        ("V", "Validé"),
        ("NV", "Non validé"),
    )
    statut= models.CharField(max_length=20, choices= statuts_choices, default= "EA")
    partenaire = models.ForeignKey(Partenaire, on_delete= models.SET_NULL, null=True, blank= True, verbose_name= "related partenaire")


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
    partenaire= models.ForeignKey(Partenaire, on_delete= models.CASCADE)

