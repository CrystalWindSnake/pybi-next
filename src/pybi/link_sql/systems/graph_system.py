from collections import deque
from typing import Dict, List


def topological_sort_kahn(graph: Dict[str, List[str]]) -> List[str]:
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
        # Output: ['D', 'E', 'B', 'F', 'C', 'A']

    """

    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    queue = deque([node for node in in_degree if in_degree[node] == 0])

    result = []

    while queue:
        current = queue.popleft()
        result.append(current)

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(graph):
        raise ValueError("Graph has cycles")

    return result[::-1]
