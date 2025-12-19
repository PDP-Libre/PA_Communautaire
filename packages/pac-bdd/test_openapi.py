def _test_swagger(url: str, swagger: str):
    """
        Vérifier si une API respecte une definition Swagger/OpenAPI

    Cette API doit respecter le versioning indiqué dans l’URL de la route API du Swagger. Dans un objectif de
    simplification le versioning des routes n’est pas affiché dans le présent document;
    Dans cette API publiée par le Fournisseur API ce dernier peut :
    •Avoir une URL spécifique en amont du versioning
    •Ajouter des propriétés aux objets dans les requêtes.
    •Ajouter des paramètres aux routes dans les requêtes.
    •Ajouter des propriétés aux objets dans les réponses.
    •Ajouter des codes erreurs dans les réponses.
    """
    raise NotImplementedError("swagger compliance non testé")



def test_swagger_flow_service():
    url = '???'
    _test_swagger(
        url,
        "docs/norme/XP_Z12-013_SWAGGER_Annexes_A_et_B_V1.2/ANNEXE A - PR XP Z12-013 - AFNOR-Flow_Service-1.1.0-swagger.json",
    )


def test_swagger_directory_service():
    url = "???"
    _test_swagger(
        url,
        "docs/norme/XP_Z12-013_SWAGGER_Annexes_A_et_B_V1.2/ANNEXE B - PR XP Z12-013 - AFNOR-Directory_Service-1.1.0-swagger.json",
    )