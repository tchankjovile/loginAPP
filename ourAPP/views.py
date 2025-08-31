from calendar import error

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, user_logged_in
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.views.decorators.http import require_POST, require_http_methods

from .forms import ModifyCandidatForm
from .models import *
import re

# Create your views here.

def validate_password_strength(password):
    """Valide la force du mot de passe"""
    if len(password) < 8:
        raise ValidationError('Le mot de passe doit contenir au moins 8 caractères')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Le mot de passe doit contenir au moins une majuscule')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Le mot de passe doit contenir au moins une minuscule')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Le mot de passe doit contenir au moins un chiffre')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Le mot de passe doit contenir au moins un caractère spécial')

# def validate_username_as_mail(username): #le but ici est de conditionner l'utilisateur à entrer son adresse mail comme nom d'utilisteur
#     if not re.search(r'@gmail.com', username):
#         raise ValidationError('vous devez mettre votre adresse mail comme nom d\'utilisateur')

def sinscrire_view(request):
    if request.method == 'POST':
        user_type= request.POST.get('user_type')
        if not user_type:
            messages.error(request, "veuillez selectionner un profil")
            return render(request, 'registration.html')
        else:
            request.session["etape1"]= user_type# le paramètre du request.session() est une clé que l'on peut utliser pour acceder à son contenu
            return redirect('sinscrire2')#le redirect() prend en paramètre le nom de l'url vers la quel on veut rediriger l'utilisateur
    return render(request, 'registration.html')

def sinscrire_view2(request):
    user_type= request.session.get('etape1')
    if not user_type:
        return redirect("sinscrire_name")
    else:
        if request.method== 'POST':

            username = request.POST.get('username', '').strip()# strip() c'est pour enlever les espace avant et après la chaines de caractère
            password = request.POST.get('password', '').strip()
            confirm_password = request.POST.get('confirm_password', '')
            telephone = request.POST.get('numero_telephone', '').strip()
            budget = request.POST.get('budget')
            errors = []

            """Valide la force du mot de passe"""
            if len(password) < 8:
                errors.append('Le mot de passe doit contenir au moins 8 caractères')
            if not re.search(r'[A-Z]', password):
                errors.append('Le mot de passe doit contenir au moins une majuscule')
            if not re.search(r'[a-z]', password):
                errors.append('Le mot de passe doit contenir au moins une minuscule')
            if not re.search(r'[0-9]', password):
                errors.append('Le mot de passe doit contenir au moins un chiffre')
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                errors.append('Le mot de passe doit contenir au moins un caractère spécial')

            # vérifie si le username est corect
            if not re.search(r'@gmail.com', username):
                errors.append('vous devez mettre votre adresse mail comme nom d\'utilisateur')

                # Validation de base
            # if budget:
            #     if budget <= 40000:
            #         errors.append('budjet non valide')

            if password != confirm_password:
                errors.append('Les mots de passe ne correspondent pas')

            if User.objects.filter(username=username).exists():
                errors.append('Ce nom d\'utilisateur est déjà pris')

            if errors:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'registration2.html', {"user_type": user_type})
            request.session["etape2"] = request.POST.dict()
            return redirect('sinscrire3')

    return render(request, 'registration2.html', {"user_type": user_type})

def sinscrire_view3(request):
    user_type = request.session.get('etape1')
    infosetape2= request.session.get('etape2')

    username = infosetape2['username']
    password = infosetape2['password']
    numero_telephone= infosetape2['numero_telephone']
    if request.method == 'POST':
        if user_type == 'candidat':
            # Validation des champs candidat
            nom = request.POST.get('nom_candidat', '').strip()
            prenom = request.POST.get('prenom', '').strip()
            ville_residence = request.POST.get('ville_residence', '').strip()
            langue_usuelle = request.POST.get('langue_usuelle', '').strip()
            budget = infosetape2['budget']
            photo_portrait = request.FILES.get('photo_portrait')
            piece_identite_recto = request.FILES.get('piece_identite_recto')
            piece_identite_verso = request.FILES.get('piece_identite_verso')
            errors= []
            if not all([photo_portrait, piece_identite_recto, piece_identite_verso]):
                errors.append('Vous devez fournir tous les fichiers')

                # Création de l'utilisateur
            if not errors:
                try:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        user_type=user_type
                    )

                    send_mail(
                        subject="Bienvenue sur notre plateforme – Votre compte est activé",
                        message=     f"Bonjour {nom},\n\n"
                            "Nous avons le plaisir de vous confirmer la création de votre compte sur notre plateforme.\n\n"
                            "Voici vos informations de connexion :\n"
                            f"- nom d'utilisateur (adresse e-mail) : {username}\n"
                            f"- Mot de passe : {password}\n\n"
                            "Afin de garantir la sécurité de votre compte, nous vous recommandons de conserver ces informations en lieu sûr "
                            "Nous vous remercions de la confiance que vous nous accordez et sommes ravis de vous accompagner dans cette expérience.\n\n"
                            "Avec toute notre considération,\n"
                            "L’équipe Support Client",
                        from_email=None,  # prendra DEFAULT_FROM_EMAIL
                        recipient_list=[username], #l'adresse mail du destinataire
                    )

                    Candidat.objects.create(
                        user=user,
                        nom=nom,
                        prenom=prenom,
                        ville_residence=ville_residence,
                        langue_usuelle=langue_usuelle,
                        budget=budget,
                        numero_telephone=numero_telephone,
                        photo_portrait=photo_portrait,
                        piece_identite_recto=piece_identite_recto,
                        piece_identite_verso=piece_identite_verso
                    )
                    for key in ['etape1', 'etape2']:
                        if key in request.session:
                            del request.session[key]  # vide la session après enregistrement

                    # Connexion automatique
                    login(request, user)
                    messages.success(request, 'Inscription réussie!')
                    return redirect('homecandidat_name')

                except Exception as e:
                    messages.error(request, f'Une erreur est survenue: {str(e)}')


        elif user_type == 'partenaire':
            # Validation des champs partenaire
            nom = infosetape2['nom']
            nom_du_centre = request.POST.get('nom_du_centre', '').strip()

            # Création de l'utilisateur
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    user_type=user_type
                )

                send_mail(
                    subject="Bienvenue parmi nos partenaires d’excellence",

                    message = f"""
                            Bonjour {nom},
            
                            Nous vous remercions chaleureusement pour la confiance que vous accordez à notre plateforme en inscrivant votre centre **{nom_du_centre}**.  
                            Votre choix témoigne de la vision et de l’ambition qui caractérisent votre organisation, et nous sommes honorés de vous compter parmi nos partenaires stratégiques.  
            
                            Voici vos identifiants de connexion :  
                            - Nom d’utilisateur : {username}  
                            - Mot de passe : {password} (gardez les précieusement!)  
            
                            En rejoignant notre réseau, **{nom_du_centre}** accède à un environnement conçu pour favoriser la réussite, stimuler la croissance et multiplier les opportunités.  
                            Soyez assuré que votre décision est un investissement gagnant : ensemble, nous partageons un objectif commun —aider vos apprenants à réussir leurs tests et réaliser leurs rêves.  
            
                            Nous sommes convaincus que ce partenariat portera des fruits remarquables, et notre équipe reste pleinement disponible pour vous.  
            
                            Avec toute notre considération,  
                            L’équipe de [INSTITUT TCF TEF EXPRESS]
                            """,

                    from_email=None,  # prendra DEFAULT_FROM_EMAIL
                    recipient_list=[username],  # l'adresse mail du destinataire
                )

                Partenaire.objects.create(
                    user=user,
                    nom=nom,
                    nom_du_centre=nom_du_centre,
                    numero_telephone=numero_telephone
                )
                for key in ['etape1', 'etape2']:
                    if key in request.session:
                        del request.session[key]  # vide la session après enregistrement

                # Connexion automatique
                login(request, user)
                messages.success(request, 'Inscription réussie!')
                return redirect('homepartenaire_name')

            except Exception as e:
                messages.error(request, f'Une erreur est survenue: {str(e)}')

    return render(request, 'registrationfinal.html', {'user_type': user_type})


def index_view(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.user_type == "candidat":
            login(request, user)
            return redirect('homecandidat_name')  # Redirige vers la page candidat
        elif user is not None and user.user_type == "partenaire":
            login(request, user)
            return redirect('homepartenaire_name')  # Redirige vers la page partnaire
        else:
            messages.error(request, 'Identifiant ou mot de passe incorrect.')
            return render(request, 'login.html')

    return render(request, 'login.html')

@login_required
def homecandidat_view(request):
    candidat=get_object_or_404(Candidat,user= request.user)
    return render(request, 'homecandidat.html', {"candidat": candidat})

@login_required
def modifycandidat_view(request):
    candidat = get_object_or_404(Candidat, user=request.user)
    print(candidat)

    if request.method == 'POST':
        form = ModifyCandidatForm(request.POST, request.FILES, instance=candidat)
        if form.is_valid():
            form.save()
            return redirect('homecandidat_name')
    else:
        form = ModifyCandidatForm(instance=candidat)  # Initialisez le formulaire avec l'instance du candidat

    return render(request, 'modifycandidat.html', {'form': form, 'candidat': candidat})


@login_required
def confirmcandidat_view(request):
    if request.user.user_type== "candidat":
        candidat= get_object_or_404(Candidat, user= request.user)
    return render(request, 'confirmationcandidat.html', {'candidat': candidat})


@login_required
def homepartenaire_view(request):
    partenaireconnecte= get_object_or_404( Partenaire, user= request.user)
    sesnotifications= Notification.objects.filter(user= request.user)
    listCandidat= Candidat.objects.filter(partenaire = partenaireconnecte.id)
    context= {
        'listCandidat': listCandidat,
        'partenaireconnecte': partenaireconnecte,
        'sesnotifications': sesnotifications,
    }
    return render(request, 'homepartenaire.html', context)

@login_required
def ajoutcandidat_view(request):
    partenaireconnecte= get_object_or_404(Partenaire, user= request.user)
    if request.method == 'POST':
        nom = request.POST.get('nom_candidat', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        numero_telephone = request.POST.get('telephone')
        ville_residence = request.POST.get('ville_residence', '').strip()
        langue_usuelle = request.POST.get('langue_usuelle', '').strip()
        budget = request.POST.get('budget')
        photo_portrait = request.FILES.get('photo_portrait')
        piece_identite_recto = request.FILES.get('piece_identite_recto')
        piece_identite_verso = request.FILES.get('piece_identite_verso')
        errors = []
        if not all([nom, prenom, ville_residence, langue_usuelle, budget]):
            errors.append('Vous devez remplir tous les champs')
        if not all([photo_portrait, piece_identite_recto, piece_identite_verso]):
            errors.append('Vous devez fournir tous les fichiers')
        Candidat.objects.create(
            partenaire= partenaireconnecte,
            nom=nom,
            prenom=prenom,
            ville_residence=ville_residence,
            langue_usuelle=langue_usuelle,
            budget=budget,
            numero_telephone=numero_telephone,
            photo_portrait=photo_portrait,
            piece_identite_recto=piece_identite_recto,
            piece_identite_verso=piece_identite_verso
        )
        return redirect('homepartenaire_name')
    return render(request, 'ajoutcandidat.html', {'partenaireconnecte': partenaireconnecte})


@login_required
def detailcandidat_view(request, candidat_id):
    partenaireconnecte = get_object_or_404(Partenaire, user=request.user)
    candidat = get_object_or_404(Candidat, id=candidat_id, partenaire=partenaireconnecte)

    if request.method == 'POST':
        # Récupération des données du formulaire
        candidat.nom = request.POST.get('nom', '').strip()
        candidat.prenom = request.POST.get('prenom', '').strip()
        candidat.numero_telephone = request.POST.get('numero_telephone', '')
        candidat.ville_residence = request.POST.get('ville_residence', '').strip()
        candidat.langue_usuelle = request.POST.get('langue_usuelle', '').strip()
        candidat.budget = request.POST.get('budget', 0)

        # Gestion des fichiers (optionnels lors de la modification)
        if 'photo_portrait' in request.FILES:
            candidat.photo_portrait = request.FILES['photo_portrait']
        if 'piece_identite_recto' in request.FILES:
            candidat.piece_identite_recto = request.FILES['piece_identite_recto']
        if 'piece_identite_verso' in request.FILES:
            candidat.piece_identite_verso = request.FILES['piece_identite_verso']

        # Validation
        errors = []
        if not all([candidat.nom, candidat.prenom, candidat.ville_residence, candidat.langue_usuelle, candidat.budget]):
            errors.append('Tous les champs obligatoires doivent être remplis')

        if not errors:
            candidat.save()
            messages.success(request, 'Les informations du candidat ont été mises à jour avec succès.')
            return redirect('detailcandidat_name', candidat_id=candidat.id)
        else:
            for error in errors:
                messages.error(request, error)

    context = {
        'partenaireconnecte': partenaireconnecte,
        'candidat': candidat,
    }
    return render(request, 'detailcandidat.html', context)

@login_required
@require_POST
def change_favoris_view(request, candidat_id):# cette vue sert à mettre un candidat en favoris
    candidat= get_object_or_404(Candidat, id= candidat_id)
    try:
        candidat = get_object_or_404(Candidat, id=candidat_id)

        # Inverser l'état du favoris
        candidat.favoris = not candidat.favoris
        candidat.save()

        return JsonResponse({
            'status': 'success',
            'favoris': candidat.favoris,
            'message': 'Favoris mis à jour avec succès'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request):
    # j'initialise mes valeurs candidat et partenaire à None
    candidat = None
    partenaire = None

    #je vérifie si la nature de l'utilisateur connecté, si c"est un candidat:
    if Candidat.objects.filter(user= request.user).exists():
        #je trouve le candidat qui correspond à l'utilisateur connecté
        candidat= get_object_or_404(Candidat, user= request.user)

    #si c'est un partenaire:
    if Partenaire.objects.filter(user= request.user):
        #je trouve le partenaire qui correspond à l'utilisateur connecté
        partenaire= get_object_or_404(Partenaire, user= request.user)

    if request.method == 'POST':
        logout(request)
        return redirect('index')

    # je prépare le contexte
    context = {
        'candidat': candidat,
        'user': request.user,
        'partenaire': partenaire,
    }
    return render(request, 'logout.html', context)

def apropos_view(request):
    pass

def contacter_view(request):
    pass

def apropos_view(request):
    pass



def deconnecter_view(request):
    pass

