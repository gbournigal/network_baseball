# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 19:44:25 2022

@author: georg
"""

import pickle
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Comparación Coberturas',
                   page_icon='https://sb.gob.do/logos/isotiposb2020.jpg', 
                   layout="wide", 
                   initial_sidebar_state="auto", 
                   menu_items=None)

df = pickle.load(open('df.obj', 'rb'))
ranking = pickle.load(open('ranking.obj', 'rb'))

players_position = pd.Series(ranking.type.values,index=ranking.player).to_dict()

def ranking_tables(ranking):
    ranking.rename(
        columns={
            'player':'Nombre',
            'PageRank_normalized':'PageRank+'
            }, inplace=True)
    table_pitchers = ranking[ranking['type']=='pitcher'][['Nombre', 'PageRank+']].reset_index(drop=True)
    table_pitchers.index += 1
    table_pitchers = table_pitchers.style.format(
        formatter={
            'Nombre':'{}',
            'PageRank+':'{:,.1f}'
            })
    table_batters =  ranking[ranking['type']=='batter'][['Nombre', 'PageRank+']].reset_index(drop=True)
    table_batters.index += 1 
    table_batters = table_batters.style.format(
        formatter={
            'Nombre':'{}',
            'PageRank+':'{:,.1f}'
            })
    return table_pitchers, table_batters


def player_stats(df, player):
    if players_position[player] == 'pitcher':
        column = 'pitcher_name'
    else:
        column = 'batter_name'
    df_player = df[df[column]==player]
    
    
col1,col2 = st.columns(2)
table_pitchers, table_batters = ranking_tables(ranking)

with col1:
    st.header('Ranking de Pitchers')
    st.table(table_pitchers)
    
with col2:
    st.header('Ranking de Bateadores')
    st.table(table_batters)