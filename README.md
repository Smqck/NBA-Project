# NBA-Project

Projet de machine learning (Polytech Clermont, IMDS) : prédire si l'équipe à domicile gagne un match NBA, et regrouper les joueurs par profil statistique.

## Structure

```
donnees/            CSV d'origine (exports Numbers, séparateur ';', 1re ligne = nom de la table)
  numbers/          fichiers Numbers d'origine
  propre/           tables nettoyées (non versionnées, voir plus bas)
scripts/
  nettoyage.py      nettoyage des tables -> donnees/propre/
notebooks/          analyses (clustering des joueurs, table joueur-saison, recherche de joueurs)
docs/               sujet, notes de travail, choix de nettoyage
```

## Recréer les tables nettoyées

`donnees/propre/` n'est pas sur GitHub (fichier > 100 Mo). Depuis la racine du projet :

```
python scripts/nettoyage.py
```
