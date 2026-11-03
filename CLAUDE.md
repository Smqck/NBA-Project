# Projet NBA : contexte pour Claude Code

Projet de cours de machine learning (cycle ingénieur, Ingénierie Mathématiques et Data Sciences, Polytech Clermont).
Travail en binôme, encadré par une professeure.

## Objectif
1. Question principale : prédire si l'équipe à domicile gagne un match, à partir des statistiques des matchs **précédents** des deux équipes (classification).
2. Étape ajoutée par la prof (fin octobre 2026) : regrouper les joueurs par profil statistique (CAH puis k-means), puis expliquer pourquoi les joueurs d'un groupe sont ensemble. À terme, ces groupes peuvent servir de variables « composition d'équipe » pour la prédiction.

## Données (dossier donnees/)
Source Kaggle « NBA games », saisons 2003-04 à 2022-23 (2022-23 incomplète : matchs jusqu'en décembre 2022).
- `games.csv` : un match par ligne (équipes, points, %, HOME_TEAM_WINS).
- `games_details.csv` : une ligne par joueur et par match (box score).
- `players.csv`, `teams.csv`, `ranking 2.csv` (classement par jour).

Format : les CSV de `donnees/` sont des exports Numbers. **1re ligne = nom de la table, séparateur `;`** (`pd.read_csv(..., sep=';', skiprows=1)`). Les notebooks du binôme lisent parfois les CSV Kaggle d'origine (séparateur `,`, sans ligne de titre) : le code doit gérer les deux.

## Structure du dossier
- `donnees/` : CSV d'origine (`games.csv`, `games_details.csv`, `players.csv`, `teams.csv`, `ranking 2.csv`) ; `donnees/numbers/` : fichiers Numbers d'origine.
- `donnees/propre/` : tables nettoyées (`games_clean.csv`, `ranking_clean.csv`, `games_details_clean.csv`, séparateur `;`). Non versionné (fichier > 100 Mo) : lancer `.venv/bin/python scripts/nettoyage.py` depuis la racine pour le recréer.
- `scripts/nettoyage.py` : nettoyage des tables. Détail des choix dans `docs/changements_nettoyage.txt`.
- `notebooks/` : `clustering_joueurs.ipynb` (regroupement des joueurs, voir plus bas), `nba-player comparatif.ipynb` (table joueur-saison 2003-2022 depuis games_details), `NBA_Player_Finder.ipynb` (recherche de joueurs similaires et 12 archétypes heuristiques, saisons 2012-2022, lit `nba_moyennes_2012_2022.csv` placé à côté du notebook). Les notebooks lisent les données dans `../donnees/` (ou `donnees/` s'ils sont lancés depuis la racine).
- `docs/` : sujet (`contexte 2.pdf`), notes de travail (`tableau.txt`, `historique_gemini.md`), `changements_nettoyage.txt`.
- `perso/` : fichiers hors projet, non versionnés.
- `.venv/` a été créé sur macOS.

## Règles de données (déjà décidées, à respecter)
- Valeurs manquantes : **les laisser en NA, ne pas les remplacer par 0** (demande de la prof). Un % sans tentative (0/0) est NA.
- Type de match : 3e caractère du `GAME_ID` sur 10 chiffres (`zfill(10)`) ; `2` = saison régulière. Les analyses joueurs utilisent la saison régulière.
- Doublons joueur-match dans games_details (289) : garder la dernière ligne (`drop_duplicates(['GAME_ID','PLAYER_ID'], keep='last')`). `games.csv` contient aussi des GAME_ID en double.
- `MIN` au format "mm:ss" (parfois "18.000000:06") ; MIN vide = joueur non entré en jeu (DNP).
- Pourcentages d'une saison : calculés sur les totaux (somme FG3M / somme FG3A), pas en moyennant les % par match.
- **Fuite d'information** : pour la prédiction, une variable ne doit utiliser que l'information disponible avant le match. Le classement d'une date inclut déjà les matchs de ce jour : prendre le classement de la **veille**.

## Partie regroupement des joueurs (état au 31/10/2026)
`clustering_joueurs.ipynb`, une saison à la fois (paramètre `SAISON`, défaut 2021 = 2021-22) :
- Table joueur-saison (transferts fusionnés), filtre `MIN_MINUTES = 500` minutes jouées ; 2022-23 exclue.
- 11 variables : PTS, AST, TO, OREB, DREB, STL, BLK ramenés à 36 minutes (stat totale × 36 / minutes totales), PART_3PTS = FG3A/FGA, PART_LF = FTA/FGA, TS = PTS / (2(FGA + 0,44 FTA)), FT_PCT. Centrées-réduites **dans chaque saison**.
- FG3_PCT n'est pas utilisé pour former les groupes (NA pour les joueurs sans tir à 3 points) ; il sert seulement à l'interprétation, NA ignorés.
- CAH (Ward) pour k = 8 à 20 : méthode du coude puis silhouette ; k = silhouette maximale entre 8 et 20. Puis k-means initialisé avec les centres de la CAH (consolidation), comparaison par ARI.
- Interprétation : carte des centres (z-scores), 3 traits dominants, joueurs les plus proches du centre, stats réelles par groupe, premier plan d'ACP (visualisation seulement).
- Résultat : pas de coude net, silhouette faible (~0,1) et presque plate entre 8 et 20, k retenu instable d'une saison à l'autre (2021-22 : k = 17). Les groupes restent lisibles (créateurs stars, meneurs passeurs, grands créateurs, protecteurs de cercle, défenseurs extérieurs, shooteurs...).
- Export : `groupes_joueurs_<SAISON>.csv`.

Points ouverts : nommer les groupes et les comparer aux 12 archétypes ; faire valider par la prof le seuil de 500 minutes et le traitement du % à 3 points (le binôme avait un FG3_PCT « ajusté » = (FG3A_TOTAL × FG3_PCT + 100 × moyenne) / (FG3A_TOTAL + 100), qui revient à mettre la moyenne quand il n'y a aucune tentative).

## Comment travailler avec nous
- Répondre en français, tutoiement, réponses proportionnées.
- Rester dans le programme du cursus (statistiques, ML classique : régression logistique, CAH, k-means, silhouette, ACP...) avec des notations simples et standard, définies avant usage.
- Code Python simple (pandas, numpy, scipy, scikit-learn, matplotlib), commenté simplement, avec une courte explication de la logique. Noms de variables en français comme dans le reste du projet.
- Quand on fournit du code, le corriger sans le réécrire entièrement.
- Ne pas modifier les CSV d'origine ; écrire les résultats dans de nouveaux fichiers.
- Ne pas commit ni push sans qu'on le demande.
