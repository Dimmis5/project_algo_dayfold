
import importG as Graph
import networkx as nx
import copy
from networkx.algorithms.community.quality import modularity
from community import community_louvain
def add_weighted_edge(G, u, v, weight):
    print ('add edge')
    print (G, u, v, weight)
    if G.has_edge(u, v):
        G[u][v]["weight"] += weight
    else:
        G.add_edge(u, v, weight=weight)

def createsuper(partition,G):
    count=0
    nG=nx.Graph()
    seen = set()
    supercommunity={}
    for key,group in partition.items():
        print (group)
        if len(group)>0:
            nG.add_node(f"c{count}")
            supercommunity[f"c{count}"]=group
            
            for node in group:
                for neigh in group:
                    edge=tuple(sorted([node,neigh]))
                    if edge not in seen:
                        seen.add(edge)
                        weight=G[neigh][node]["weight"] if G.has_edge(node, neigh) else 0
                        add_weighted_edge(nG,f"c{count}",f"c{count}", weight)
        count+=1

            
            
    return [supercommunity,nG]
def belongcom(node,com):
    print ('belong com')
    for key,group in com.items():
        if node in group:
            return key
    return 
"""G c est le grpahe de base pour soutirer tous les poids relier a une communaute"""
def supergroup(partition,G):
    print('supergroup')
    seen = set()
    super= createsuper(partition,G)
    print (partition)
    print (super)
    """prend chaque noeud d une partition"""
    for key,group in super[0].items():
          print(group)
          print(len(group))
          if len(group)>0:
             weight=0
             """regarde chacun des voisins"""
             for node in group:
                li=list(G.neighbors(node))
                """pour chaque voisin regarde les voisins exterieurs et qui ne sont pas dans la communaute"""
                for neigh in li :
                    if neigh not in group :
                     print (key)
                     edge=tuple(sorted([node,neigh]))
                     if edge not in seen:
                        seen.add(edge)
                        print (neigh,node)
                        """ajoute le poid de chaque noeud sur l arrete communaute actuelle et celle du coisin"""
                        weight=G[neigh][node]["weight"] if G.has_edge(node, neigh) else 0
                        add_weighted_edge(super[1],key,belongcom(neigh,super[0]), weight)
    
                  
    print("===== NOEUDS =====")
    for node in super[1].nodes():
        print(node)

    print("===== ARÊTES =====")
    for u, v, data in super[1].edges(data=True):
        print(u, "--", v, "poids =", data.get("weight", 1))
    print(super)
    return super

              
                
