import importG as Graph
import networkx as nx
import copy
from networkx.algorithms.community.quality import modularity
from community import community_louvain
import supergroup as sup
EPSILON = 1e-10


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

print(m)
"""[0]:modularite et [1]:dictionnaire de commuanute"""
maxmod=[-2,0]
"""max est la configuration qui maximise la modularite """
max=0
Ak=0
"""prend un graphe le transforme en dicntionnaire"""
def createcommunity(G):
    community={}
    for n in G.nodes():
         community[n]=[n]
    return community
"""verifie s ils appartiennent a la meme communaute"""
def belong(n1,n2,community):
    if n2 in community[n1]:
        return 
    return 0

community=createcommunity(G)
print(community)
def fcom(nt,community):
    copy_comm = copy.deepcopy(community)
    for c in copy_comm:
        if nt in copy_comm[c]:
            old=copy_comm[c]
    return old
def shift(n1, nt, community):
    
    copy_comm = copy.deepcopy(community)

    """ trouver la communauté actuelle de nt"""
    for c in copy_comm:
        if nt in copy_comm[c]:
            copy_comm[c].remove(nt)
            old=copy_comm[c]
        
    """ trouver la communauté de n1"""
    for c in copy_comm:
        if n1 in copy_comm[c]:
            copy_comm[c].append(nt)
            new=copy_comm[c]

    return [copy_comm,old,new]
"""calcul par communaute"""
def mod(community,G):
    m = G.size(weight="weight")
    p1=0
    for k1,v in community.items():
        for v1 in v:
            for v2 in v:
                    k_i = G.degree(v1, weight="weight")
                    k_j = G.degree(v2, weight="weight")
                    w=G[v2][v1]["weight"] if G.has_edge(v1, v2) else 0
                    p1+=(w-((k_i*k_j)/(2*m)))

    return (1/(2*m))*p1

def modlocal(community,G):
    p1=0
    m = G.size(weight="weight")
    for v1 in community:
        for v2 in community:
                
                k_i = G.degree(v1, weight="weight")
                k_j = G.degree(v2, weight="weight")
          
                w=G[v2][v1]["weight"] if G.has_edge(v1, v2) else 0
                p1+=(w-((k_i*k_j)/(2*m)))
    return (1/(2*m))*p1

oldsupergroup=0
def stabilisation(newcommunity,maxmod,count,G):
    print("//////////////////////////")
    print(maxmod)
    oldmax=maxmod[0]
    refreshmax=maxmod
    for key,value in newcommunity.items():
        for n in value:
            li=list(G.neighbors(n))
            for t in li:
                if (n!=t):
                    oldQ=fcom(t,newcommunity)
                    newQ=fcom(n,newcommunity)
                    oldmod=modlocal(oldQ,G)
                    newmod=modlocal(newQ,G)
                    clone=shift(n,t,newcommunity)
                    """print(modlocal(clone[1]))
                    print(modlocal(clone[2]))
                    print (modlocal(clone[1])+modlocal(clone[2])-oldmod-newmod)
                    print(oldmax)"""
                    dmodu=oldmax+modlocal(clone[1],G)+modlocal(clone[2],G)-oldmod-newmod
                    
                    """print(dmodu)"""
                    if refreshmax[0]<dmodu:
                        refreshmax=(dmodu,clone[0])
                
                   
                    """
                    communities = list(clone[0].values())  
                    print('bonne mdoularite')
                    print(mod(clone[0],G))
                    print(modularity(G, communities, weight="weight"))
                    print(clone)
                    """
                  
    return [oldmax,refreshmax]
   

def boucle (newcommunity,maxmod,count,G):
     stab=stabilisation(newcommunity,maxmod,count,G)
     print ("stab")
     """[0]:oldmax qui est la modularite de depart c est a dire avant satbilisation  celle qui permet de verifier qu il ya eu un changement [1][0]:modularite qui vient d etre calculer apres stabilisation,[1][1]communaute apres stabilisation"""
     print (stab)
     
     if abs(stab[1][0] - stab[0]) < EPSILON:
        print('arrete')
        print(count)
        partition = community_louvain.best_partition(G,weight="weight")
        print (maxmod)
        print(partition)
        print(maxmod[1])

        supergroup=sup.supergroup(stab[1][1],G)
        supercommunity=createcommunity(supergroup[1])
        """print(sup.supergroup(maxmod[1],G))"""
        print('supergroup')
        print(supergroup)
        """mod est applique sur un dictionnaire de communaute"""
  
        print("===== NOEUDS =====")
        for node in supergroup[1].nodes():
            print(node)

        print("===== ARÊTES =====")
        for u, v, data in supergroup[1].edges(data=True):
            print(u, "--", v, "poids =", data.get("weight", 1))
        print(mod(supercommunity,supergroup[1]))
        newstab=stabilisation(supercommunity,[mod(supercommunity,supergroup[1]),supercommunity],0,supergroup[1])
        
        if (abs(mod(supercommunity,supergroup[1])-mod(newstab[1][1],supergroup[1])))<EPSILON:
            print('fin')
            print(supergroup)
            return supergroup 
        else :
            boucle(supercommunity,[mod(supercommunity,supergroup[1]),supercommunity],0,supergroup[1])
     community=stab[1][1]
     count+=1
     boucle(community,stab[1],count,G)
        

"""liste des voisins"""
for key,value in community.items():
    for n in value:
        li=list(G.neighbors(n))
        for t in li:
            clone=shift(n,t,community)
            modu=mod(clone[0],G)
            if maxmod[0]<modu:
                maxmod=(modu,clone[0])
            communities = list(clone[0].values())
            """print(modularity(G, communities, weight="weight"))
            print(clone)"""

oldcommunity=community

community=maxmod[1]
print (oldcommunity)
print (maxmod)
print(boucle(community,maxmod,0,G))


""" sinon tourne en boucle
    if abs(maxmod[0] - oldmax) < EPSILON:
        print('arrete')
        print(count)
        partition = community_louvain.best_partition(G,weight="weight")
        print (maxmod)
        print(partition)
        print(maxmod[1])

        supergroup=sup.supergroup(maxmod[1],G)
        print(sup.supergroup(maxmod[1],G))
        print(mod(maxmod[1]))
        print(mod(supergroup[0]))
        newstab=stabilisation(supergroup[0],supergroup[1],0)
        
        if (mod(supergroup[0])-mod(maxmod[1]))<EPSILON:
            return 
        else :
            stabilisation(supergroup[0],supergroup[1],0)
        
        return 
    community=maxmod[1]
    count+=1
    stabilisation(community,maxmod,count)"""