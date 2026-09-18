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

## Sondes disponibles

### Etat du mineur

| Entite | Description |
| --- | --- |
| `binary_sensor.<mineur>_en_ligne` | Indique si le mineur repond et si au moins une hashboard est vivante. |

### Performance et pool

| Entite | Unite | Description |
| --- | --- | --- |
| `sensor.<mineur>_hashrate_total` | `KSol/s` | Hashrate total retourne par le mineur. |
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
| `sensor.<mineur>_hashboard_1_temperature` | `°C` | Temperature de la hashboard 1. |
| `sensor.<mineur>_hashboard_2_hashrate` | `KSol/s` | Hashrate de la hashboard 2. |
| `sensor.<mineur>_hashboard_2_temperature` | `°C` | Temperature de la hashboard 2. |
| `sensor.<mineur>_hashboard_3_hashrate` | `KSol/s` | Hashrate de la hashboard 3. |
| `sensor.<mineur>_hashboard_3_temperature` | `°C` | Temperature de la hashboard 3. |

Les sondes de hashrate par hashboard exposent aussi des attributs utiles : statut, moyenne 1 minute, moyenne 5 minutes, moyenne 15 minutes, accepted, rejected et hardware errors.

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

## Version

Version actuelle : `0.1.1`.
