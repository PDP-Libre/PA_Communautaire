# language: fr
Fonctionnalité: trackingId
    Section 5.2.2 de XP_Z12-013.pdf 
    Le Fournisseur API doit accepter un ‘trackingId’ et le stocker.
    Ce paramètre doit être optionnel pour le Client API.
    Il permet à ce dernier de retrouver plus facilement le flux avec son propre identifiant interne.
    Le Fournisseur API ne doit pas contrôler l’unicité de cet identifiant qui est un identifiant interne au Client API.    

    Scénario: trackingId fourni
        Etant un utilisateur

        Quand j'appele l'API POST /flows
        Et que je joins le fichier /data/FA-3647.pdf
        Et que la propriété trackingId est 11111111

        Alors j'obtiens le statut #accepted


    Scénario: trackingId absent
        Etant un utilisateur

        Quand j'appele l'API POST /flows
        Et que je joins le fichier /data/FA-3647.pdf

        Alors j'obtiens le statut #accepted


    Scénario: trackingId doublon
        Etant un utilisateur

        Quand j'appele l'API POST /flows
        Et que je joins le fichier /data/FA-3647.pdf
        Et que la propriété trackingId est 11111111

        Alors j'obtiens le statut #accepted

        Quand j'appele l'API POST /flows
        Et que je joins le fichier /data/FA-3648.pdf
        Et que la propriété trackingId est 11111111

        Alors j'obtiens le statut #accepted
