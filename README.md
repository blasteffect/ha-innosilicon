# Home Assistant Innosilicon Miner

Integration Home Assistant personnalisee pour superviser un ASIC Innosilicon en local.

Modeles compatibles :

- Innosilicon A9 ZMaster
- Innosilicon A9+ ZMaster+
- Innosilicon A9++ ZMaster

L'integration interroge l'API du mineur, s'authentifie avec les identifiants fournis dans Home Assistant, puis met a jour les sondes toutes les 30 secondes.

## Fonctionnalites

- Configuration depuis l'interface Home Assistant, sans YAML obligatoire.
- Communication locale avec le mineur via son API HTTP.
- Authentification par utilisateur et mot de passe.
- Rafraichissement automatique des donnees toutes les 30 secondes.
- Re-authentification automatique si le jeton expire.
- Regroupement des entites sous un appareil Home Assistant Innosilicon.
- Lien direct vers l'interface de configuration du mineur depuis l'appareil.
- Capteurs de hashrate instantane, 1 minute, 5 minutes et 15 minutes.
- Detail des pools detectes par le mineur.
- Configuration de trois pools depuis les options de l'integration.
- Bouton pour appliquer la configuration des pools au mineur.
- Bouton pour redemarrer le mineur.

## Sondes disponibles

### Etat du mineur

| Entite | Description |
| --- | --- |
| `binary_sensor.<mineur>_en_ligne` | Indique si le mineur repond et si au moins une hashboard est vivante. |

### Performance et pool

| Entite | Unite | Description |
| --- | --- | --- |
| `sensor.<mineur>_hashrate_total` | `KSol/s` | Hashrate total retourne par le mineur. |
| `sensor.<mineur>_hashrate_1m` | `KSol/s` | Hashrate moyen sur 1 minute. |
| `sensor.<mineur>_hashrate_5m` | `KSol/s` | Hashrate moyen sur 5 minutes. |
| `sensor.<mineur>_hashrate_15m` | `KSol/s` | Hashrate moyen sur 15 minutes. |
| `sensor.<mineur>_pool_active` | - | Pool stratum actuellement actif. |
| `sensor.<mineur>_accepted` | - | Total des shares acceptees sur les hashboards. |
| `sensor.<mineur>_rejected` | - | Total des shares rejetees sur les hashboards. |
| `sensor.<mineur>_hardware_errors` | - | Total des erreurs materielles remontees par les hashboards. |
| `sensor.<mineur>_ventilateur` | `%` | Pourcentage de fonctionnement du ventilateur. |

### Hashboards

Une paire de sondes est creee automatiquement pour chaque hashboard detectee par le mineur.

| Entite | Unite | Description |
| --- | --- | --- |
| `sensor.<mineur>_hashboard_1_hashrate` | `KSol/s` | Hashrate de la hashboard 1. |
| `sensor.<mineur>_hashboard_1_hashrate_1m` | `KSol/s` | Hashrate moyen 1 minute de la hashboard 1. |
| `sensor.<mineur>_hashboard_1_hashrate_5m` | `KSol/s` | Hashrate moyen 5 minutes de la hashboard 1. |
| `sensor.<mineur>_hashboard_1_hashrate_15m` | `KSol/s` | Hashrate moyen 15 minutes de la hashboard 1. |
| `sensor.<mineur>_hashboard_1_temperature` | `°C` | Temperature de la hashboard 1. |
| `sensor.<mineur>_hashboard_2_hashrate` | `KSol/s` | Hashrate de la hashboard 2. |
| `sensor.<mineur>_hashboard_2_hashrate_1m` | `KSol/s` | Hashrate moyen 1 minute de la hashboard 2. |
| `sensor.<mineur>_hashboard_2_hashrate_5m` | `KSol/s` | Hashrate moyen 5 minutes de la hashboard 2. |
| `sensor.<mineur>_hashboard_2_hashrate_15m` | `KSol/s` | Hashrate moyen 15 minutes de la hashboard 2. |
| `sensor.<mineur>_hashboard_2_temperature` | `°C` | Temperature de la hashboard 2. |
| `sensor.<mineur>_hashboard_3_hashrate` | `KSol/s` | Hashrate de la hashboard 3. |
| `sensor.<mineur>_hashboard_3_hashrate_1m` | `KSol/s` | Hashrate moyen 1 minute de la hashboard 3. |
| `sensor.<mineur>_hashboard_3_hashrate_5m` | `KSol/s` | Hashrate moyen 5 minutes de la hashboard 3. |
| `sensor.<mineur>_hashboard_3_hashrate_15m` | `KSol/s` | Hashrate moyen 15 minutes de la hashboard 3. |
| `sensor.<mineur>_hashboard_3_temperature` | `°C` | Temperature de la hashboard 3. |

Les sondes de hashrate par hashboard exposent aussi des attributs utiles : statut, moyenne 1 minute, moyenne 5 minutes, moyenne 15 minutes, accepted, rejected et hardware errors.

### Details des pools

Une serie de sondes est creee pour chaque pool retourne par le mineur :

| Entite | Description |
| --- | --- |
| `sensor.<mineur>_pool_1_url` | URL du pool 1. |
| `sensor.<mineur>_pool_1_user` | Utilisateur du pool 1. |
| `sensor.<mineur>_pool_1_status` | Etat du pool 1. |
| `sensor.<mineur>_pool_1_accepted` | Shares acceptees sur le pool 1. |
| `sensor.<mineur>_pool_1_rejected` | Shares rejetees sur le pool 1. |

Les memes sondes sont exposees pour les pools 2 et 3 si le mineur les retourne.

### Commandes

| Entite | Description |
| --- | --- |
| `button.<mineur>_redemarrer` | Demande un redemarrage du mineur via `/api/reboot`. |
| `button.<mineur>_appliquer_les_pools` | Envoie la configuration des pools via `/api/updatePools`. |

## Installation

Copiez le dossier `custom_components/innosilicon` dans le dossier `custom_components` de Home Assistant, puis redemarrez Home Assistant.

Avec HACS en depot personnalise :

1. Ajoutez ce depot comme integration personnalisee.
2. Installez `Innosilicon Miner`.
3. Redemarrez Home Assistant.

## Configuration dans Home Assistant

1. Ouvrez `Parametres` > `Appareils et services`.
2. Cliquez sur `Ajouter une integration`.
3. Recherchez `Innosilicon Miner`.
4. Renseignez l'adresse IP ou le nom DNS du mineur.
5. Renseignez l'utilisateur et le mot de passe du mineur.

L'utilisateur par defaut propose est `admin`.

### Configuration des pools

Depuis les options de l'integration, vous pouvez renseigner jusqu'a trois pools :

- URL du pool
- utilisateur
- mot de passe

Une fois les options enregistrees, utilisez le bouton `Appliquer les pools` pour envoyer la configuration au mineur.

## Carte Lovelace

Exemple de carte `entities` pour afficher les informations principales du mineur :

```yaml
type: entities
entities:
  - entity: binary_sensor.innominer1_lan_en_ligne
    name:
    type: entity
  - entity: sensor.innominer1_lan_hashrate_total
    name:
    type: entity
  - entity: sensor.innominer1_lan_pool_active
    name:
    type: entity
  - entity: sensor.innominer1_lan_accepted
    name:
    type: entity
  - entity: sensor.innominer1_lan_rejected
    name:
    type: entity
  - entity: sensor.innominer1_lan_hashboard_1_temperature
    name:
    type: entity
  - entity: sensor.innominer1_lan_hashboard_2_temperature
    name:
    type: entity
  - entity: sensor.innominer1_lan_hashboard_3_temperature
    name:
    type: entity
title: innominer1
```

### Rendu attendu

La carte affiche un resume lisible du mineur :

| Libelle | Exemple |
| --- | --- |
| En ligne | Connecte |
| Hashrate total | `88,715 KSol/s` |
| Pool active | `mining.viabtc.io` |
| Accepted | `13` |
| Rejected | `1` |
| Hashboard 1 temperature | `66,0 °C` |
| Hashboard 2 temperature | `65,0 °C` |
| Hashboard 3 temperature | `66,0 °C` |

## Historique

### v0.2.0 - En cours

- Ajout des capteurs de hashrate moyen 1 minute, 5 minutes et 15 minutes.
- Ajout des capteurs de detail des pools : URL, utilisateur, statut, accepted et rejected.
- Ajout de la configuration de trois pools depuis les options de l'integration.
- Ajout du bouton `Appliquer les pools` pour envoyer la configuration au mineur.
- Ajout du bouton `Redemarrer` via l'endpoint `/api/reboot`.
- Amelioration de l'API interne avec les endpoints `/api/ping`, `/api/reboot` et `/api/updatePools`.
- Gestion du retour `token: expired` avec nouvelle authentification automatique.

### v0.1.1

- Documentation complete des fonctionnalites et sondes exposees.
- Ajout de l'exemple de carte Lovelace pour Home Assistant.
- Ajout du rendu attendu de la carte dans le README.
- Ajout de l'icone de l'integration.
- Precision des modeles compatibles : A9 ZMaster, A9+ ZMaster+ et A9++ ZMaster.

### v0.1.0

- Premiere version fonctionnelle de l'integration.
- Configuration depuis l'interface Home Assistant.
- Authentification locale sur l'API du mineur.
- Remontee de l'etat en ligne du mineur.
- Ajout des sondes principales : hashrate total, pool actif, accepted, rejected, erreurs materielles, ventilateur et temperatures des hashboards.
- Creation automatique des entites par hashboard detectee.

## Version

Version actuelle : `0.2.0`.
