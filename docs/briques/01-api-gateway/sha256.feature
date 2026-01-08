# language: fr
Fonctionnalité: Contrôle sha256
    Section 5.2.3 de XP_Z12-013.pdf 

    Scénario: Contrôle sha256
        Etant un utilisateur

        Quand j'appele l'API POST /flows
        Et que je joins le fichier /data/FA-3647.pdf
        Et que la propriété sha256 est 5b43e7fece64fdf6953cc686e5ea63c086329b77ed4e96d5be35ff1c1bae8717

        Alors j'obtiens le statut #rejected
