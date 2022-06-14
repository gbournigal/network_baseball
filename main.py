# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 19:44:10 2022

@author: georg
"""

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


def get_df():
    df = statcast(start_dt='2022-04-07', 
                  end_dt='2022-06-13',
                  verbose=True)[['batter', 'pitcher', 'events']]
    df = df[df['events'].notna()]
    return df
  

def player_names(df):
    player_ids = list(dict.fromkeys(list(df['batter'].unique()) + list(df['pitcher'].unique())))
    
    player_names = playerid_reverse_lookup(player_ids, key_type='mlbam')
    player_names['name'] = player_names['name_first'] + ' ' + player_names['name_last']
    return player_names[['key_mlbam', 'name']]


def prepare_df(df, player_names):
    df_prueba = df.merge(player_names, how='left', left_on='batter', right_on='key_mlbam').rename(
        columns={'name':'batter_name'}).merge(
            player_names, how='left', left_on='pitcher', right_on='key_mlbam').rename(
                columns={'name':'pitcher_name'}).drop(
                    columns=['key_mlbam_x', 'key_mlbam_y'])
                    
    ## ohtani fix
    df_prueba['batter_name'] = np.where(df_prueba['batter_name'].isin(df_prueba["pitcher_name"]),
                                        df_prueba['batter_name'] + ' (batter)',
                                        df_prueba['batter_name'])
    
    df_prueba['pitcher_name'] = np.where(df_prueba['pitcher_name'].isin(df_prueba["batter_name"]),
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
    
    df_prueba = df_prueba.dropna()
    df_prueba['losser'] = np.where(
        df_prueba['winner']==df_prueba['batter_name'],
        df_prueba['pitcher_name'],
        df_prueba['batter_name']) 
    
    df_prueba['value_plays'] = np.where(
        df_prueba['events'] == 'home_run',
        4,
        np.where(
            df_prueba['events'].isin(['double','strikeout']),
            2,
            np.where(
                df_prueba['events'] == 'tirple',
                3,
                1),
        ))
    
    df_edges = df_prueba[['winner', 'losser', 'value_plays']]
    return df_prueba, df_edges


def get_ranking(df, edges):
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
    
    ranking = nx.pagerank(G, weight='value_plays')
    ranking = pd.DataFrame.from_dict([ranking]).transpose().sort_values(0,
                                                                        ascending=False).reset_index().rename(
        columns={0: 'PageRank',
                 'index':'player'}).merge(
                     players_df, how='left', left_on='player', right_on='player')
    
    ranking['PageRank_normalized'] = np.where(
        ranking['type']=='pitcher',
        ranking['PageRank']/float(ranking[ranking['type']=='pitcher'].mean())*100,
        ranking['PageRank']/float(ranking[ranking['type']=='batter'].mean())*100
        )
    return ranking


def main():
    df_orig = get_df()
    names = player_names(df_orig)
    df, edges = prepare_df(df_orig, names)
    ranking = get_ranking(df, edges)
    return df, ranking
    
    
df, ranking = main()