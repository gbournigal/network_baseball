# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 11:36:16 2022

@author: gbournigal
"""

import streamlit as st


st.set_page_config(
     page_title="""Baseball Network Ranking""",
     page_icon="⚾",
     layout="wide",
 )

st.title("""⚾Baseball Network Ranking""")

st.write("""
         The following baseball app utilizes data from [Baseball Savant](https://baseballsavant.mlb.com/statcast_searchcalculate) to calculate two new stats:
             
         - **SabrRank+**: It is calculated by adding up the difference between positive and negative outcomes for each batter versus pitcher confrontation over the season, using [Tom Tango's Linear Weights](http://www.tangotiger.net/RE9902event.html) to define the value of each outcome. 
                             The score is then normalized to ensure that the average batter/pitcher has a 100 score.
        
         - **PageRank+**: involves building a graph based on the interactions between pitchers and batters, with links being created depending on the outcome of each matchup. These links are weighted using Tom Tango's Linear Weights, and the
                             [PageRank Algorithm](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html#networkx.algorithms.link_analysis.pagerank_alg.pagerank) is then applied with personalized values on the nodes based on SabrRank+ results. The PageRank values are also normalized to give the average batter/pitcher a score of 100.
         
         These stats provide crucial insights into player performance, with SabrRank+ revealing which players are performing well overall, and PageRank+ showing which batters are dominating against top pitchers and which pitchers are getting the upper hand against top batters. To see how your favorite players stack up, open the sidebar and navigate to the Rank Visualization in the top left corner.
         """)