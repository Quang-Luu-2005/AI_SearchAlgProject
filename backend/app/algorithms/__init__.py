"""Search algorithm implementations for FloodRoute HCMC."""

from ..core.contracts import AlgorithmName
from .unweighted import breadth_first_search, depth_first_search
from .greedy import greedy_best_first_search
from .bidirectional import bidirectional_search

from .weighted import (
    ALGORITHM_REGISTRY,
    a_star_search,
    resolve_algorithm,
    uniform_cost_search,
)

ALGORITHM_REGISTRY[AlgorithmName.BFS] = breadth_first_search
ALGORITHM_REGISTRY[AlgorithmName.DFS] = depth_first_search
ALGORITHM_REGISTRY[AlgorithmName.GREEDY] = greedy_best_first_search
ALGORITHM_REGISTRY[AlgorithmName.BIDIRECTIONAL] = bidirectional_search

__all__ = [
    "ALGORITHM_REGISTRY",
    "a_star_search",
    "resolve_algorithm",
    "uniform_cost_search",
    "breadth_first_search",
    "depth_first_search",
    "greedy_best_first_search",
    "bidirectional_search",
]
