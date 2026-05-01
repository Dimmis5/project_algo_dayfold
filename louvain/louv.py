import importG as Graph
import networkx as nx
import copy
from networkx.algorithms.community.quality import modularity
from community import community_louvain


G=Graph.G
m=Graph.sum

"""
G = nx.Graph()

# Ajout des arêtes avec poids
G.add_edge("A", "B", weight=3)
G.add_edge("A", "C", weight=2)
G.add_edge("B", "C", weight=4)
G.add_edge("C", "D", weight=1)
G.add_edge("D", "E", weight=5)
G.add_edge("B", "E", weight=2)
m=3+2+4+1+5+2
"""

"""" la somme des poids sur chaque noeud"""
dic=Graph.dic

print(m)
maxmod=[-2,0]
"""max est la configuration qui maximise la modularite"""
max=0
Ak=0
"""prend un graphe le transforme en dicntionnaire"""
def community(G):
    community={}
    for n in G.nodes():
         community[n]=[n]
    return community
"""verifie s ils appartiennent a la meme communaute"""
def belong(n1,n2,community):
    if n2 in community[n1]:
        return 1
    return 0

community=community(G)
print(community)
def fcom(nt,community):
    copy_comm = copy.deepcopy(community)
    for c in copy_comm:
        if nt in copy_comm[c]:
            old=copy_comm[c]
    return old
def shift(n1, nt, community):
    
    copy_comm = copy.deepcopy(community)

    # trouver la communauté actuelle de nt
    for c in copy_comm:
        if nt in copy_comm[c]:
            copy_comm[c].remove(nt)
            old=copy_comm[c]
        
    # trouver la communauté de n1
    for c in copy_comm:
        if n1 in copy_comm[c]:
            copy_comm[c].append(nt)
            new=copy_comm[c]

    return [copy_comm,old,new]
"""calcul par communaute"""
def mod(community):
    p1=0
    for k1,v in community.items():
        for v1 in v:
            for v2 in v:
                    k_i = G.degree(v1, weight="weight")
                    k_j = G.degree(v2, weight="weight")
                    w=G[v2][v1]["weight"] if G.has_edge(v1, v2) else 0
                    p1+=(w-((k_i*k_j)/(2*m)))

    return (1/(2*m))*p1

def modlocal(community):
    p1=0
    for v1 in community:
        for v2 in community:
                k_i = G.degree(v1, weight="weight")
                k_j = G.degree(v2, weight="weight")
                w=G[v2][v1]["weight"] if G.has_edge(v1, v2) else 0
                p1+=(w-((k_i*k_j)/(2*m)))
    return (1/(2*m))*p1

def supergroup():
    return
def stabilisation(oldcommunity,newcommunity,maxmod,count):
    print("//////////////////////////")
    oldmax=maxmod[0]
    for key,value in newcommunity.items():
        for n in value:
            li=list(G.neighbors(n))
            for t in li:
                if (n!=t):
                    oldQ=fcom(t,newcommunity)
                    newQ=fcom(n,newcommunity)
                    oldmod=modlocal(oldQ)
                    newmod=modlocal(newQ)
                    clone=shift(n,t,newcommunity)
                    print(modlocal(clone[1]))
                    print(modlocal(clone[2]))
                    print (modlocal(clone[1])+modlocal(clone[2])-oldmod-newmod)
                    print(oldmax)
                    dmodu=oldmax+modlocal(clone[1])+modlocal(clone[2])-oldmod-newmod
                    
                    print(dmodu)
                    if maxmod[0]<dmodu:
                        maxmod=(dmodu,clone[0])
                
                    communities = list(clone[0].values())
                    print('bonne mdoularite')
                    print(mod(clone[0]))
                    print(modularity(G, communities, weight="weight"))
                    print(clone)
    if maxmod[0]==oldmax:
        print('arrete')
        print(count)
        partition = community_louvain.best_partition(G,weight="weight")
        print (maxmod)
        print(partition)
        return
    
    community=maxmod[1]
    count+=1
    stabilisation(newcommunity,community,maxmod,count)


"""liste des voisins"""
for key,value in community.items():
    for n in value:
        li=list(G.neighbors(n))
        for t in li:
            clone=shift(n,t,community)
            modu=mod(clone[0])
            if maxmod[0]<modu:
                maxmod=(modu,clone[0])
            communities = list(clone[0].values())
            """print(modularity(G, communities, weight="weight"))
            print(clone)"""

oldcommunity=community

community=maxmod[1]
print (oldcommunity)
print (maxmod)

stabilisation(oldcommunity,community,maxmod,0)
    
