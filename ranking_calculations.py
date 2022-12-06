# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 19:44:10 2022

@author: georg
"""

import pickle
import pandas as pd
import networkx as nx
import numpy as np
from pybaseball import statcast, playerid_reverse_lookup

## values of plays
batter_wins = ['single', 
               'walk', 
               'double',
               'home_run',
               'triple',
               'hit_by_pitch']

pitcher_wins = ['field_out',
                'strikeout',
                'force_out',
                'grounded_into_double_play',
                'field_error',
                'fielders_choice',
                'double_play',
                'other_out']

plays_values = {
    'single': 0.474,
    'walk': 0.33,
    'double': 0.764,
    'triple': 1.063,
    'home_run': 1.409,
    'hit_by_pitch': 0.385,
    'field_out': 0.299,
    'strikeout': 0.31,
    'force_out': 0.299,
    'grounded_into_double_play': 0.299,
    'field_error': 0.299,
    'fielders_choice': 0.299,
    'double_play': 0.299,
    'other_out': 0.299
    }


def get_df():
    df = statcast(start_dt='2022-04-06', 
                  end_dt='2022-08-03',
                  verbose=True)
    [['batter', 'pitcher', 'events']]
    df = df[df['events'].notna()]
    return df
  

def player_names(df):
    player_ids = list(dict.fromkeys(list(df['batter'].unique()) + list(df['pitcher'].unique())))
    
    player_names = playerid_reverse_lookup(player_ids, key_type='mlbam')
    player_names['name'] = player_names['name_first'] + ' ' + player_names['name_last'] + '-' + player_names['key_mlbam'].astype(str)
    return player_names[['key_mlbam', 'name']]


def prepare_df(df, player_names):
    df_prueba = df.merge(player_names, how='left', left_on='batter', right_on='key_mlbam').rename(
        columns={'name':'batter_name'}).merge(
            player_names, how='left', left_on='pitcher', right_on='key_mlbam').rename(
                columns={'name':'pitcher_name'}).drop(
                    columns=['key_mlbam_x', 'key_mlbam_y'])
                    
    ## ohtani fix
    
    batter_names = df_prueba['batter_name'].copy()
    pitcher_names = df_prueba['pitcher_name'].copy()
    df_prueba['batter_name'] = np.where(df_prueba['batter_name'].isin(pitcher_names),
                                        df_prueba['batter_name'] + ' (batter)',
                                        df_prueba['batter_name'])
    
    df_prueba['pitcher_name'] = np.where(df_prueba['pitcher_name'].isin(batter_names),
                                        df_prueba['pitcher_name'] + ' (pitcher)',
                                        df_prueba['pitcher_name'])
    
    
    
    
    ## network df
    df_prueba['winner'] = np.where(
        df_prueba['events'].isin(batter_wins),
        df_prueba['batter_name'],
        np.where(
            df_prueba['events'].isin(pitcher_wins),
            df_prueba['pitcher_name'],
            np.NaN
            )
        )
    
    df_prueba = df_prueba.dropna(subset=['winner'])
    df_prueba['losser'] = np.where(
        df_prueba['winner']==df_prueba['batter_name'],
        df_prueba['pitcher_name'],
        df_prueba['batter_name']) 
    
    df_prueba = df_prueba.dropna(subset=['losser'])
    
    df_prueba['value_plays'] = df_prueba['events']
    df_prueba['value_plays'] = df_prueba['value_plays'].replace(plays_values)
    
    df_edges = df_prueba[['winner', 'losser', 'value_plays']]
    return df_prueba, df_edges


def get_ranking(df, edges, personalization=None):
    players_df = pd.DataFrame()
    players_df['player'] =  list(dict.fromkeys(list(df['batter_name'].unique()) + list(df['pitcher_name'].unique())))
    players_df['type'] = np.where(players_df['player'].isin(df['batter_name']),
                                    'batter',
                                    'pitcher') 
    
    
    G = nx.convert_matrix.from_pandas_edgelist(edges,
                                               source='losser',
                                               target='winner',
                                               edge_attr='value_plays',
                                               create_using=nx.DiGraph
                                               )
    
    ranking = nx.pagerank(G, 
                          weight='value_plays',
                          personalization=personalization
                          )
    ranking = pd.DataFrame.from_dict([ranking]).transpose().sort_values(0,
                                                                        ascending=False).reset_index().rename(
        columns={0: 'PageRank',
                 'index':'player'}).merge(
                     players_df, how='left', left_on='player', right_on='player')
    
    ranking['PageRank_normalized'] = np.where(
        ranking['type']=='pitcher',
        ranking['PageRank']/float(ranking[ranking['type']=='pitcher']['PageRank'].mean())*100,
        ranking['PageRank']/float(ranking[ranking['type']=='batter']['PageRank'].mean())*100
        )
    return ranking


def add_rankings_to_df(df, ranking):
    return df.merge(ranking[['player', 'PageRank_normalized']], how='left', 
                 left_on='batter_name', right_on='player').drop('player', axis=1).rename(
                     columns={
                         'PageRank_normalized':'PageRank_batter'}).merge(
                             ranking[['player', 'PageRank_normalized']],
                             how='left',
                             left_on='pitcher_name', right_on='player').drop('player', axis=1).rename(
                                 columns={
                                     'PageRank_normalized':'PageRank_pitcher'})


def personalization_values(edges):
    per_dict = {}
    counter = 0
    for i in edges.winner.append(edges.losser).unique():
        print(counter/1324*100)
        counter += 1
        positive = edges[edges['winner'] == i]['value_plays'].sum()
        negative = edges[edges['losser'] == i]['value_plays'].sum()
        per_dict[i] = positive - negative
    
    minimum = min(per_dict.values())
    for i in per_dict.keys():
        per_dict[i] = per_dict[i] + abs(minimum) + 1
    return per_dict
        

def ranking_results():
    df_orig = get_df()
    names = player_names(df_orig)
    df, edges = prepare_df(df_orig, names)
    personalization = personalization_values(edges)
    ranking = get_ranking(df, edges, personalization)
    df = add_rankings_to_df(df, ranking)
    for i in ['batter_name', 'pitcher_name', 'winner', 'losser']:
        df[i] = df[i].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace('[^a-zA-Z.() ]', '')
    ranking['SabrRank+'] = ranking['player'].replace(personalization)
    ranking['SabrRank+'] = np.where(
        ranking['type']=='pitcher',
        ranking['SabrRank+']/float(ranking[ranking['type']=='pitcher']['SabrRank+'].mean())*100,
        ranking['SabrRank+']/float(ranking[ranking['type']=='batter']['SabrRank+'].mean())*100
        )
    ranking['player'] = ranking.player.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace('[^a-zA-Z.() ]', '')
    pickle.dump(df,open('df.obj', 'wb'))
    pickle.dump(ranking,open('ranking.obj', 'wb'))


if __name__=='__main__':
    ranking_results()
    