# Specs ESB central

Les briques communiquent via un [bus de message ESB](https://en.wikipedia.org/wiki/Enterprise_service_bus) centralisé.

Les briques ne peuvent communiquer entre elles directement.


```mermaid
flowchart TD
    01-api-gateway <--> 02-esb-central  
    03-controle-formats <--> 02-esb-central
    04-validation-metier <--> 02-esb-central
    05-conversion-formats <--> 02-esb-central
    06-annuaire-local <--> 02-esb-central
    07-routage <--> 02-esb-central
    08-transmission-fiscale <--> 02-esb-central
    09-gestion-cycle-vie <--> 02-esb-central
```

Pour pouvoir communiquer chaque brique doit définir au moins un canal d'entrée.
Chaque message déposé sur ce canal déclenchera une action.
Le résultat est déposé sur un autre canal.
