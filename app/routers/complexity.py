from fastapi import APIRouter
import time
import random
import math
from models import DayfoldGraph, CategoryNode
from algorithms.bfs_suggest_friends import suggest_friends
from algorithms.category_tree import find_category
from algorithms.louvain import louvain
from algorithms.PPR import PersonalizedPageRank, Graph, NodeType, build_graph_from_dayfold

router = APIRouter(prefix="/complexity", tags=["complexity"])

def generate_random_graph(n_users, n_edges):
    graph = DayfoldGraph()
    for i in range(1, n_users + 1):
        graph.add_user(i, f"User{i}")
    
    users_ids = list(range(1, n_users + 1))
    for _ in range(n_edges):
        u1 = random.choice(users_ids)
        u2 = random.choice(users_ids)
        if u1 != u2:
            graph.add_friendship(u1, u2)
    return graph

import random

def generate_random_tree(n_nodes):
    root = CategoryNode(name="Root", cat_id=0)
    nodes = [root]
    
    for i in range(1, n_nodes):
        parent = random.choice(nodes)
        
        child = CategoryNode(name=f"Node{i}", cat_id=i)
        if parent.children is None:
            parent.children = []
        parent.children.append(child)
        
        nodes.append(child)
        
    return root, nodes

@router.get("/benchmark/bfs")
def benchmark_bfs(n_max: int = 1000, steps: int = 10):
    results = []
    step_size = max(1, n_max // steps)
    first_time = None
    first_n = None

    for n in range(100, n_max + 1, step_size):
        random.seed(n)
        m = n * 5
        graph = generate_random_graph(n, m)
        
        start_time = time.perf_counter()
        for _ in range(5):
            suggest_friends(graph, 1)
        end_time = time.perf_counter()
        
        avg_time = (end_time - start_time) / 5
        current_time_ms = avg_time * 1000

        if first_time is None:
            first_time = current_time_ms
            first_n = n

        theoretical_time = (first_time / first_n) * n
        results.append({
            "n": n,
            "time": round(current_time_ms, 4),
            "theoretical": round(theoretical_time, 4),
            "label": f"N={n}"
        })
    return results

@router.get("/benchmark/tree")
def benchmark_tree(n_max: int = 1000, steps: int = 10):
    results = []
    step_size = max(1, n_max // steps)
    first_time = None
    first_n = None

    for n in range(100, n_max + 1, step_size):
        random.seed(n)
        root, nodes = generate_random_tree(n)
        target = nodes[-1].name 
        start_time = time.perf_counter()
        for _ in range(10):
            find_category(root, target)
        end_time = time.perf_counter()
        
        avg_time = (end_time - start_time) / 10
        current_time_ms = avg_time * 1000

        if first_time is None:
            first_time = current_time_ms
            first_n = n

        theoretical_time = (first_time / first_n) * n
        results.append({
            "n": n,
            "time": round(current_time_ms, 4),
            "theoretical": round(theoretical_time, 4),
            "label": f"N={n}"
        })
    return results

@router.get("/benchmark/louvain")
def benchmark_louvain(n_max: int = 300, steps: int = 10):
    results = []
    step_size = max(1, n_max // steps)
    first_time = None
    first_n = None

    for n in range(50, n_max + 1, step_size):
        random.seed(n)
        m = n * 3
        graph = generate_random_graph(n, m)
        
        start_time = time.perf_counter()
        louvain(graph)
        end_time = time.perf_counter()
        
        current_time_ms = (end_time - start_time) * 1000

        if first_time is None:
            first_time = current_time_ms
            first_n = n


        theoretical_time = first_time * (n * math.log(n)) / (first_n * math.log(first_n))
        
        results.append({
            "n": n,
            "time": round(current_time_ms, 4),
            "theoretical": round(theoretical_time, 4),
            "label": f"N={n}"
        })
    return results

@router.get("/benchmark/ppr")
def benchmark_ppr(n_max: int = 500, steps: int = 10):
    results = []
    step_size = max(1, n_max // steps)
    first_time = None
    first_n = None

    for n in range(50, n_max + 1, step_size):
        random.seed(n)
        m = n * 4
        dayfold_graph = generate_random_graph(n, m)
        g = build_graph_from_dayfold(dayfold_graph)
        ppr = PersonalizedPageRank(g, max_iter=20) 
        
        start_time = time.perf_counter()
        ppr.run("1")
        end_time = time.perf_counter()
        
        current_time_ms = (end_time - start_time) * 1000

        if first_time is None:
            first_time = current_time_ms
            first_n = n

        theoretical_time = (first_time / first_n) * n
        
        results.append({
            "n": n,
            "time": round(current_time_ms, 4),
            "theoretical": round(theoretical_time, 4),
            "label": f"N={n}"
        })
    return results
