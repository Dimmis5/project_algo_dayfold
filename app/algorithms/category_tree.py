from models import CategoryNode

def find_category(root: CategoryNode, name: str) -> CategoryNode:
    if root.name == name:
        return root
    
    for child in root.children:
        found = find_category(child, name)
        if found:
            return found
    return None

def get_category_path(node: CategoryNode) -> list:
    path = []
    current = node
    while current:
        path.append(current.name)
        current = current.parent
    return path[::-1] 

def display_hierarchy(node: CategoryNode, level: int = 0):
    print("  " * level + "|-- " + node.name)
    for child in node.children:
        display_hierarchy(child, level + 1)