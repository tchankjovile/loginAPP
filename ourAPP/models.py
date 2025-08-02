from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError(' le champ "username" soit être activé')
        user= self.model(username= username)
        user.set_password(password)
        user.save(using= self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser):
    USER_TYPE_CHOICES= (
        ('admin', 'administrateur'),
         ('partenaire', 'partenaire'),
        ('candidat', 'candidat'),
    )
    username= models.CharField(max_length=150, unique = True)

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
    numero_telephone= models.IntegerField()

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
    telephone= models.IntegerField()
    photo_portrait= models.ImageField(upload_to='photo/portrait/', help_text= "L'image doit être clair, de préférence avec fond blanc")
    piece_identite= models.ImageField(upload_to='photo/piecesidentite/', help_text="La piece fdoit être à jour et les informations doivent être lisibles")
    confirmation = models.ImageField(upload_to= 'photo/confirmation/')
    ville_residence= models.CharField(max_length= 150)
    langue_usuelle= models.CharField(max_length= 150)
    favoris= models.BooleanField(default= False)
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
    telephone= models.IntegerField()
    def __str__(self):
        return f"{self.nom} {self.score}"

