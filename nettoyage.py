"""
Nettoyage des tables du projet NBA.

Lit les CSV exportés depuis Numbers (dossier CSV/) et écrit les versions
nettoyées dans CSV/propre/. Les fichiers d'origine ne sont pas modifiés.

Lancer depuis le dossier du projet :
    .venv/bin/python nettoyage.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

DOSSIER = Path(__file__).parent / 'CSV'
SORTIE = DOSSIER / 'propre'

TYPES_MATCH = {'1': 'Pre-saison', '2': 'Saison reguliere', '3': 'All-Star',
               '4': 'Playoffs', '5': 'Play-in'}


def lire(nom_fichier):
    # Export Numbers : 1re ligne = nom de la table, séparateur ';'
    return pd.read_csv(DOSSIER / nom_fichier, sep=';', skiprows=1, low_memory=False)


def ecrire(df, nom_fichier):
    df.to_csv(SORTIE / nom_fichier, sep=';', index=False)
    print(f'  -> {nom_fichier} : {len(df)} lignes, {df.shape[1]} colonnes\n')


def bilan_en_pourcentage(bilan):
    """'10-3' -> (10, 3, 0.769). Avant le 1er match ('0-0'), le pourcentage vaut NaN."""
    victoires, defaites = bilan.str.split('-', expand=True).astype(float).T.values
    joues = victoires + defaites
    pct = np.where(joues > 0, victoires / np.where(joues > 0, joues, 1), np.nan)
    return victoires, defaites, pct


# ---------------------------------------------------------------- GAMES
def nettoyer_games():
    print('GAMES')
    games = lire('games.csv')
    n = len(games)

    # Colonnes inutiles : toujours "Final" / doublons de HOME_TEAM_ID et VISITOR_TEAM_ID
    games = games.drop(columns=['GAME_STATUS_TEXT', 'TEAM_ID_home', 'TEAM_ID_away'])

    games = games.drop_duplicates('GAME_ID')
    print(f'  {n - len(games)} matchs en double supprimés')

    n = len(games)
    games = games.dropna(subset=['PTS_home', 'PTS_away'])
    print(f'  {n - len(games)} matchs sans statistiques supprimés')

    games['GAME_DATE_EST'] = pd.to_datetime(games['GAME_DATE_EST'])
    games['TYPE_MATCH'] = games['GAME_ID'].astype(str).str[0].map(TYPES_MATCH)
    games = games.sort_values(['GAME_DATE_EST', 'GAME_ID'])

    ecrire(games, 'games_clean.csv')


# -------------------------------------------------------------- RANKING
def nettoyer_ranking():
    print('RANKING')
    ranking = lire('ranking 2.csv')
    n = len(ranking)

    # LEAGUE_ID : que des 0 / RETURNTOPLAY : spécifique à la bulle Covid 2019-2020
    ranking = ranking.drop(columns=['LEAGUE_ID', 'RETURNTOPLAY'])

    ranking = ranking.drop_duplicates(['TEAM_ID', 'STANDINGSDATE'])
    print(f'  {n - len(ranking)} lignes en double (même équipe, même date) supprimées')

    # SEASON_ID = 1er chiffre (type de saison) + année, ex. 22022
    ranking['TYPE_SAISON'] = ranking['SEASON_ID'].astype(str).str[0].map(TYPES_MATCH)
    ranking['SEASON'] = ranking['SEASON_ID'].astype(str).str[1:].astype(int)

    # Bilans "victoires-défaites" -> nombres + pourcentage
    for col, prefixe in [('HOME_RECORD', 'HOME'), ('ROAD_RECORD', 'ROAD')]:
        v, d, pct = bilan_en_pourcentage(ranking[col])
        ranking[f'{prefixe}_W'] = v
        ranking[f'{prefixe}_L'] = d
        ranking[f'{prefixe}_W_PCT'] = pct

    ranking['STANDINGSDATE'] = pd.to_datetime(ranking['STANDINGSDATE'])
    ranking = ranking.sort_values(['STANDINGSDATE', 'TEAM_ID'])

    ecrire(ranking, 'ranking_clean.csv')


# -------------------------------------------------------- GAMES_DETAILS
def minutes_en_decimal(valeur):
    """'18:06' ou '18.000000:06' (bug d'export Numbers) -> 18.1"""
    if pd.isna(valeur):
        return np.nan
    texte = str(valeur)
    if ':' in texte:
        mn, sec = texte.split(':')
        return float(mn) + float(sec) / 60
    return float(texte)


def nettoyer_games_details():
    print('GAMES_DETAILS')
    details = lire('games_details.csv')
    n = len(details)

    details = details.drop_duplicates(['GAME_ID', 'PLAYER_ID'])
    print(f'  {n - len(details)} lignes en double (même joueur, même match) supprimées')

    details['MIN'] = details['MIN'].map(minutes_en_decimal)

    aberrant = (details['MIN'] < 0) | (details['MIN'] > 70) | (details['PF'] > 6)
    print(f'  {aberrant.sum()} lignes aberrantes supprimées (minutes < 0 ou > 70, plus de 6 fautes)')
    details = details[~aberrant]

    # Joueurs sur la feuille de match mais pas entrés en jeu (DNP) : on les garde,
    # ils peuvent servir à repérer les absences. Colonne pour les filtrer facilement.
    details['A_JOUE'] = details['MIN'] > 0
    print(f'  {(~details["A_JOUE"]).sum()} lignes de joueurs non entrés en jeu (gardées, A_JOUE = False)')

    details['TYPE_MATCH'] = details['GAME_ID'].astype(str).str[0].map(TYPES_MATCH)

    ecrire(details, 'games_details_clean.csv')


if __name__ == '__main__':
    SORTIE.mkdir(exist_ok=True)
    nettoyer_games()
    nettoyer_ranking()
    nettoyer_games_details()
