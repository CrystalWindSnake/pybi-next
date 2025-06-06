from collections import deque
from typing import Dict, List


def topological_sort_kahn(graph: Dict[str, List[str]]) -> Dict[str, int]:
    """

    Example:
    .. code-block:: python
        graph = {
            "A": ["B", "C"],
            "B": ["D", "E"],
            "C": ["F"],
            "D": [],
            "E": [],
            "F": [],
        }
        topological_sort_kahn(graph)

        # Output: {'F': 3, 'E': 3, 'D': 3, 'C': 2, 'B': 2, 'A': 1}

    """

    in_degree = {node: 0 for node in graph}
    level = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    queue: deque[str] = deque()

    for node in in_degree:
        if in_degree[node] == 0:
            queue.append(node)
            level[node] = 1

    result = []

    while queue:
        current = queue.popleft()
        result.append(current)

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1

            if level[current] + 1 > level[neighbor]:
                level[neighbor] = level[current] + 1

            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(graph):
        raise ValueError("Graph has cycles")

    return {name: level[name] for name in result[::-1]}
