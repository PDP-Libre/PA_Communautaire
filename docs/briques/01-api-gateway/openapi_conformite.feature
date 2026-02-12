# language: fr
Fonctionnalité: Conformité API XP Z12-013
    Vérifier que le swagger exposé par la PA est conforme
    à la norme AFNOR XP Z12-013.
    Référence : docs/norme/XP_Z12-013.pdf
    Swagger de référence : docs/norme/XP_Z12-013_SWAGGER_Annexes_A_et_B_V1.2/

    Scénario: Conformité Flow Service
        Soit une pa communautaire
        Quand je vérifie la conformité swagger "flow"
        Alors le swagger est conforme

    Scénario: Conformité Directory Service
        Soit une pa communautaire
        Quand je vérifie la conformité swagger "directory"
        Alors le swagger est conforme
