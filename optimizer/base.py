from abc import ABC, abstractmethod
from typing import List, Dict
from models.point import Point
from models.route import Route

class RoutingAlgorithm(ABC):
    @abstractmethod
    def construct_routes(self, depot: Point, points: List[Point], max_capacity: int) -> List[Route]:
        """Construct vehicle routes for given points."""
        pass
    
    def get_route_summary(self, routes: List[Route]) -> Dict:
        """Get a summary of the constructed routes."""
        total_capacity = sum(route.capacity_used for route in routes)
        return {
            'num_routes': len(routes),
            'total_capacity_used': total_capacity,
            'routes': [
                {
                    'route_id': i,
                    'points': [point.coordinates for point in route.path],
                    'capacity_used': route.capacity_used
                }
                for i, route in enumerate(routes)
            ]
        }