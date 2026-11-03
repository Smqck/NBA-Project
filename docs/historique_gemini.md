# Historique du projet (résumé rédigé par Gemini, 14/10/2026)

## 1. Sujet et objectif
- Prédire si l'équipe à domicile gagne (classification), à partir des stats des matchs précédents des deux équipes.
- Consignes, rendu, date limite : non abordés.
- Outils : Python (Pandas), éventuellement R en fin de projet. Travail collaboratif via Git / VS Code.

## 2. Données
- Tables : `games`, `ranking`, `teams`, `games_details`, `players`. Explorées en profondeur : `ranking` et `games`.
- `ranking` (classement quotidien) : colonnes importantes `TEAM_ID`, `STANDINGSDATE`, `CONFERENCE`, `W_PCT`, `HOME_RECORD`, `ROAD_RECORD`.
  - À supprimer : `RETURNTOPLAY` (spécifique bulle Covid), `LEAGUE_ID` (que des 0).
  - `HOME_RECORD` / `ROAD_RECORD` au format "10-3" → à convertir en pourcentage.
- `games` : colonnes importantes `GAME_DATE_EST`, `SEASON`, `HOME_TEAM_ID`, `VISITOR_TEAM_ID`, `HOME_TEAM_WINS` (cible).
  - À supprimer : `TEAM_ID_home` / `TEAM_ID_away` (doublons), `GAME_STATUS_TEXT` (toujours "Final").
  - Fuite de données : `PTS_`, `FG_PCT_`, `AST_`, `REB_`… sont des stats de fin de match, inutilisables telles quelles.

## 3. Étapes réalisées
1. Modèle relationnel : `TEAM_ID` comme clé de liaison.
2. Choix des colonnes à garder ou supprimer (voir ci-dessus).
3. Cible : `HOME_TEAM_WINS` (1 = victoire à domicile).
4. Stratégie de feature engineering :
   - moyennes glissantes (ex. 5 derniers matchs) des stats de `games` ;
   - double jointure `games` ↔ `ranking` sur `[TEAM_ID + date]`, une fois pour l'équipe à domicile, une fois pour l'équipe visiteuse.
5. Conflit Git résolu sur `tableau.txt`.

## 4. Code écrit
```python
import pandas as pd

ranking_df[['HOME_WINS', 'HOME_LOSSES']] = ranking_df['HOME_RECORD'].str.split('-', expand=True).astype(float)
ranking_df['HOME_WIN_PCT'] = ranking_df['HOME_WINS'] / (ranking_df['HOME_WINS'] + ranking_df['HOME_LOSSES'])
ranking_df['HOME_WIN_PCT'] = ranking_df['HOME_WIN_PCT'].fillna(0)
```

## 5. Résultats
Aucun modèle entraîné : le projet en est à la préparation des données.

## 6. Décisions
- Moyennes glissantes plutôt que stats brutes, pour éviter la fuite de données.
- Jointure composite équipe + date, pour éviter un produit cartésien.
- Variable « différentiel » : écart de `W_PCT` entre l'équipe à domicile et l'équipe visiteuse.

## Nouvelle consigne de la prof (rendez-vous d'avancement, octobre 2026)
Avant l'étape finale (prédiction), faire une **classification des joueurs selon leurs statistiques** : regrouper les joueurs par style de jeu (ex. 3&D) pour pouvoir trouver un joueur « qui joue comme X » mais moins fort et moins cher (exemple de la prof : un club qui veut un profil Mbappé sans pouvoir se le payer).

**Décisions (14/10/2026)** : salaires à voir avec la prof la semaine suivante ; comparaison des joueurs saison par saison. Répartition : l'utilisateur s'occupe du nettoyage des tables, son collègue de l'analyse.
**Fait** : `nettoyage.py` crée `CSV/propre/` (games_clean, ranking_clean, games_details_clean). Environnement Python : `.venv/`.

## 7. Reste à faire
- Coder la double jointure `games` ↔ `ranking`.
- Coder les moyennes glissantes sur 5 matchs.
- Questions ouvertes : début de saison (win rate peu fiable, piste : classement de la saison précédente) ; utilisation de `games_details` (joueurs absents via `COMMENT`), `teams`, `players` ; choix des modèles (régression logistique, Random Forest, XGBoost…).
