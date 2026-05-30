
import networkx as nx
import copy
from networkx.algorithms.community.quality import modularity
from community import community_louvain
from . import supergroup as sup
EPSILON = 1e-10

import networkx as nx

from models import DayfoldGraph


def build_interaction_weights(graph: DayfoldGraph) -> nx.Graph:
    interaction_graph = nx.Graph()

    for user_id, user in graph.users.items():
        interaction_graph.add_node(
            user_id,
            username=user.username,
            name=user.name,
            email=user.email,
        )

    def add_weight(u1, u2, weight):
        if u1 == u2:
            return
        if interaction_graph.has_edge(u1, u2):
            interaction_graph[u1][u2]["weight"] += weight
        else:
            interaction_graph.add_edge(u1, u2, weight=weight)

    for user_id, user in graph.users.items():
        for followed in user.following:
            add_weight(user_id, followed.user_id, 5)

        for pin_id in getattr(user, "liked_pins", set()):
            pin = graph.find_pin(pin_id)
            if pin:
                for other_user_id in pin.liked_by:
                    add_weight(user_id, other_user_id, 2)

        for pin_id in getattr(user, "saved_pins", set()):
            pin = graph.find_pin(pin_id)
            if pin:
                for other_user_id in pin.saved_by:
                    add_weight(user_id, other_user_id, 3)

        for pin_id in getattr(user, "shared_pins", set()):
            pin = graph.find_pin(pin_id)
            if pin:
                for other_user_id in pin.shared_by:
                    add_weight(user_id, other_user_id, 4)

    return interaction_graph


"""
G=Graph.G
m=Graph.sum
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
                    if v1 == v2:
                        w *= 2
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
                    dmodu=mod(clone[0],G)
                    communities = [
                    nodes
                     for nodes in clone[0].values()
                     if len(nodes) > 0
                    ]

                    print(clone)
                    print("mod maison :", dmodu)
                    print("mod NetworkX :", modularity(G, communities, weight="weight"))
                    print("différence :", abs(dmodu - modularity(G, communities, weight="weight")))
                    print(clone)
                    print(dmodu)
                    if refreshmax[0]<dmodu:
                        print('changement')
                        refreshmax=(dmodu,clone[0])
                
                   
                    """
                    communities = list(clone[0].values())  
                    print('bonne mdoularite')
                    print(mod(clone[0],G))
                    print(modularity(G, communities, weight="weight"))
                    print(clone)
                    """
                  
    return [oldmax,refreshmax]

def newloop(newcommunity, maxmod, count, G):
    """
    Lance la stabilisation jusqu'à ce que la modularité n'augmente plus.
    Retourne le meilleur résultat : [modularité, communauté]
    """

    stab = stabilisation(newcommunity, maxmod, count, G)

    old_mod = stab[0]
    new_mod = stab[1][0]

    if abs(new_mod - old_mod) < EPSILON:
        return stab[1]

    community = stab[1][1]
    count += 1

    return newloop(community, stab[1], count, G)

def merge(result, G):
    """
    Transforme les communautés trouvées en super-graphe.

    result = [modularité, communauté]
    G = graphe actuel

    Retourne :
    - supercommunity : communauté initiale du super-graphe
    - supermaxmod : [modularité, supercommunity]
    - superG : super-graphe
    """

    community = result[1]

    supergroup = sup.supergroup(community, G)

    superG = supergroup[1]

    # Chaque super-nœud commence seul dans sa communauté
    supercommunity = createcommunity(superG)

    super_mod = mod(supercommunity, superG)

    supermaxmod = [super_mod, supercommunity]

    return supercommunity, supermaxmod, superG

def partloop(newcommunity, maxmod, count, G):
    """
    Boucle complète Louvain multi-niveaux :
    1. stabilisation locale
    2. création du super-graphe
    3. relance sur le super-graphe
    4. arrêt si la modularité n'augmente plus
    """

    # Phase locale sur le graphe actuel
    result = newloop(newcommunity, maxmod, count, G)

    old_mod = result[0]

    # Création du super-graphe
    supercommunity, supermaxmod, superG = merge(result, G)

    # Phase locale sur le super-graphe
    result_super = newloop(supercommunity, supermaxmod, 0, superG)

    new_mod = result_super[0]
    print(new_mod)
    print(old_mod)
    if new_mod  <=old_mod+ EPSILON:
        print("fin Louvain")
        print("modularité finale :", old_mod)
        print("communautés finales :", result[1])

        return result, G
    print('partloop')
    return partloop(result_super[1], result_super, 0, superG)

def louvain(graph: DayfoldGraph) :

    """[0]:modularite et [1]:dictionnaire de commuanute"""
    maxmod=[-2,0]
    G = build_interaction_weights(graph)
    community=createcommunity(G)
    print(community)
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

    result, final_graph = partloop(community, maxmod, 0, G)

    print("Résultat final :")
    print(result)

    print("Graphe final :")
    print(final_graph.nodes())
    print(final_graph.edges(data=True))
    return result[1]