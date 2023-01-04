# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 19:44:25 2022

@author: georg
"""

import pickle
import pandas as pd
import streamlit as st

st.title("""🥇Ranking Viewer""")


df = pickle.load(open('df.obj', 'rb'))
ranking = pickle.load(open('ranking.obj', 'rb'))

radio_side = st.radio('How to display tables:', ['top-bottom', 'side-side'])
    
players_position = pd.Series(ranking.type.values,index=ranking.player).to_dict()

def ranking_tables(ranking):
    ranking.rename(
        columns={
            'player':'Nombre',
            'PageRank_normalized':'PageRank+'
            }, inplace=True)
    table_pitchers = ranking[ranking['type']=='pitcher'][['Nombre', 'PageRank+', 'SabrRank+']].reset_index(drop=True)
    table_pitchers.index += 1
    table_pitchers['SabrRank+ #'] = table_pitchers['SabrRank+'].rank(ascending=False)
    table_pitchers = table_pitchers.style.format(
        formatter={
            'Nombre':'{}',
            'PageRank+':'{:,.1f}',
            'SabrRank+': '{:,.1f}',
            'SabrRank+ #': '{:,.0f}'
            })
    table_batters =  ranking[ranking['type']=='batter'][['Nombre', 'PageRank+', 'SabrRank+']].reset_index(drop=True)
    table_batters.index += 1 
    table_batters['SabrRank+ #'] = table_batters['SabrRank+'].rank(ascending=False)
    table_batters = table_batters.style.format(
        formatter={
            'Nombre':'{}',
            'PageRank+': '{:,.1f}',
            'SabrRank+': '{:,.1f}',
            'SabrRank+ #': '{:,.0f}'
            })
    return table_pitchers, table_batters


# def player_stats(df, player):
#     if players_position[player] == 'pitcher':
#         column = 'pitcher_name'
#     else:
#         column = 'batter_name'
#     df_player = df[df[column]==player]
    
table_pitchers, table_batters = ranking_tables(ranking)
if radio_side == 'side-side':
    col1,col2 = st.columns(2)
    
    with col1:
        st.header('Ranking de Pitchers')
        st.dataframe(table_pitchers, use_container_width=True)
        
    with col2:
        st.header('Ranking de Bateadores')
        st.dataframe(table_batters, use_container_width=True)

else:
    st.header('Ranking de Pitchers')
    st.dataframe(table_pitchers, use_container_width=True)    
    st.header('Ranking de Bateadores')
    st.dataframe(table_batters, use_container_width=True)
    
with st.expander("See comments on the results"):
    st.write("""
             The tables feature the ranking for the PageRank+ statistic on their indices.
             
             Jose Berrios is a particularly interesting case among pitchers, as he saw a significant improvement in ranking from position 359 in SabrRank+ to 4 in PageRank+. Despite having a subpar season overall, Berrios seemed to excel at dominating top batters. Other pitchers who saw notable improvements in ranking include Tarik Skubal (going from 37 to 9), Adam Wainwright (48 to 15), and Robbie Ray (106 to 25). In contrast, pitchers like Justin Verlander, Aaron Nola, and Spencer Strider experienced declines in ranking, with Verlander going from 3 to 50, Nola from 6 to 42, and Strider from 12 to 54.
                 
            On the batters side, Aaron Judge was the top performer in both rankings. Some batters saw notable improvements in ranking, such as Corey Seager (going from 214 to 16), Eugenio Suarez (308 to 19), and Bo Bichette (553 to 23). However, other batters experienced declines in ranking, including Paul Goldschmidt (2 to 24), Rafael Devers (6 to 28), and Matt Carpenter (7 to 201).
                 
             """)