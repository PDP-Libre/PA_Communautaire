# Specs brique stockage



```mermaid
flowchart TD
    01-api-gateway <--> 10-stockage
    03-controle-formats <--> 10-stockage
    04-validation-metier <--> 10-stockage
    05-conversion-formats <--> 10-stockage
    06-annuaire-local <--> 10-stockage
    07-routage <--> 10-stockage
    08-transmission-fiscale <--> 10-stockage
    09-gestion-cycle-vie <--> 10-stockage
```

TODO:
* quels fichiers stocker ?
* stockage cloud
* hebergement souverain
* permettre un stockage chez le client
* estimer la volumetrie ?
* estimer le cout si cloud
* quel fournisseeur souverain ? scaleway ? OVH ? hetzner ?