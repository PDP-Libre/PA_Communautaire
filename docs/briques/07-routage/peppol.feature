# language: fr
Fonctionnalité: Requêtes PEPPOL
    PEPPOL est un service DNS.
    Je dois pouvoir interroger ce service
    et obtenir les informations utiles au routage des factures.
    Pour celà je dois savoir construire une requête DNS PEPPOL.


    Scénario: md5
        L'algorithme de calcul d'empreinte (hash) md5 est utilisé
        pour *masquer* l'identifiant de l'entreprise.

        Quand je calcule l'empreinte md5 de "bonjour!"
        Alors j'obtiens "6c2675d749449f2c8af1216fd866bb54"

        Quand je calcule l'empreinte md5 de "Ceci est un contenu beaucoup plus long pour montrer que l'empreinte ne dépends pas de la taille du message."
        Alors j'obtiens "bd12e833704eebbb40305f0e727a3612"

        Quand je calcule l'empreinte md5 de "0002::123456789"
        Alors j'obtiens "7e144582b3307ab3868c6c2835c582f6"

        Quand je calcule l'empreinte md5 de "0009::123456789"
        Alors j'obtiens "8874539cbfa5af29d56194be355ac1b1"


    Scénario: Identification France
        L'entreprise Française peut être identifiée de différentes façons

        Alors l'identification par SIRET porte le code "0002"
        Alors l'identification par SIREN porte le code "0009"
        Alors l'identification par TVA_FR porte le code "9957"


    Scénario: Empreinte participant
        L'empreinte participant dépends de l'identifiant et de son code

        Quand je calcule l'empreinte SIREN "222222222"
        Alors j'obtiens "3ddb2999105b666703fc700e14885016"

        Quand je calcule l'empreinte SIRET "222222222"
        Alors j'obtiens "6dbdf4f29451b37456ca48b550bdbaee"

        Quand je calcule l'empreinte TVA_FR "222222222"
        Alors j'obtiens "d0d6bafc0317e3e8baa9504a9a022f9c"


    Scénario: Hôte SML
        Le nom d'hôte pour la requête DNS est calculé à partir de l'empreinte et d'une racine SML.

        Soit la racine SML "ma.racine.local"

        Quand je calcule l'hôte SML pour SIREN "222222223"
        Alors j'obtiens "B-82b2b8c47a173b4be5e428bf8e5be1dc.iso6523-actorid-upis.ma.racine.local"

        Quand je calcule l'hôte SML pour SIRET "222222222"
        Alors j'obtiens "B-6dbdf4f29451b37456ca48b550bdbaee.iso6523-actorid-upis.ma.racine.local"

        Quand je calcule l'hôte SML pour TVA_FR "222222222"
        Alors j'obtiens "B-d0d6bafc0317e3e8baa9504a9a022f9c.iso6523-actorid-upis.ma.racine.local"


        Soit la racine SML "acc.edelivery.tech.ec.europa.eu"

        Quand je calcule l'hôte SML pour SIREN "222222222"
        Alors j'obtiens "B-3ddb2999105b666703fc700e14885016.iso6523-actorid-upis.acc.edelivery.tech.ec.europa.eu"

        Quand je calcule l'hôte SML pour SIRET "222222222"
        Alors j'obtiens "B-6dbdf4f29451b37456ca48b550bdbaee.iso6523-actorid-upis.acc.edelivery.tech.ec.europa.eu"

        Quand je calcule l'hôte SML pour TVA_FR "222222222"
        Alors j'obtiens "B-d0d6bafc0317e3e8baa9504a9a022f9c.iso6523-actorid-upis.acc.edelivery.tech.ec.europa.eu"


        # Soit l'entreprise #e1 avec le SIREN "123456789"
        # Et l'entreprise #e1 enregistrée sur PEPPOL
        # Quand j'interroge le SML via DNS
        # Alors j'obtiens une réponse DNS valide
        # Et j'obtiens l'URL du SMP "https://smp.pa-distante.fr"

