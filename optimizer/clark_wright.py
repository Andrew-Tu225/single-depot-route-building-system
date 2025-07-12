from typing import List, Tuple, Set, Optional
import itertools
from .base import RoutingAlgorithm
from models.point import Point
from models.route import Route
from models.saving_pair import SavingPair
from distance.base import DistanceCalculator
from distance.euclidean import EuclideanDistanceCalculator
from optimizer.route_utils import arrive_time_estimator
class ClarkWrightAlgorithm(RoutingAlgorithm):
    def __init__(self, distance_calculator: DistanceCalculator = None):
        self.distance_calculator = distance_calculator or EuclideanDistanceCalculator()
    
    def calculate_saving(self, depot: Point, p1: Point, p2: Point) -> float:
        """Calculate the savings for combining two points into one route."""
        dist_depot_p1 = self.distance_calculator.calculate_distance(depot, p1)
        dist_depot_p2 = self.distance_calculator.calculate_distance(depot, p2)
        dist_p1_p2 = self.distance_calculator.calculate_distance(p1, p2)
        
        return dist_depot_p1 + dist_depot_p2 - dist_p1_p2
    
    def generate_savings_list(self, depot: Point, points: List[Point]) -> List[SavingPair]:
        """Generate and sort all possible savings pairs."""
        savings_list = []
        
        for p1, p2 in itertools.combinations(points, 2):
            saving_value = self.calculate_saving(depot, p1, p2)
            savings_list.append(SavingPair(p1, p2, saving_value))
        
        # Sort by saving value in descending order
        savings_list.sort(key=lambda x: x.saving_value, reverse=True)
        return savings_list
    
    def find_routes_with_edge_point(self, point: Point, routes: List[Route]) -> List[int]:
        """Find all routes that have the given point as an edge point."""
        route_indices = []
        for i, route in enumerate(routes):
            if point in route.edge_points:
                route_indices.append(i)
        return route_indices
    
    def is_interior_point(self, point: Point, routes: List[Route]) -> bool:
        """Check if a point is an interior point in any route."""
        for route in routes:
            if point in route.interior_points:
                return True
        return False
    
    def get_edge_insertion_info(self, point: Point, route: Route) -> Tuple[Optional[Point], Optional[int]]:
        """Get information about where to insert a point in a route."""
        if not route.edge_points:
            return None, None
        
        if route.start_point == point:
            return route.start_point, 0
        elif route.end_point == point:
            return route.end_point, route.size - 1
        
        return None, None
    
    def get_insert_point_and_position(self, point_pair: Tuple[Point, Point], route: Route) -> Tuple[Optional[Point], Optional[int]]:
        """
        Determine which point to insert and at which position in the route.
        Returns (point_to_insert, insertion_position)
        """
        p1, p2 = point_pair
        
        if p1 in route.edge_points:
            edge_point = p1
            insert_point = p2
        elif p2 in route.edge_points:
            edge_point = p2
            insert_point = p1
        else:
            return None, None
        
        # Determine insertion position
        if route.start_point == edge_point:
            return insert_point, 0
        elif route.end_point == edge_point:
            return insert_point, route.size
        
        return None, None
    
    def merge_routes(self, routes: List[Route], route1_idx: int, route2_idx: int, 
                    connecting_points: Tuple[Point, Point]) -> List[Route]:
        """
        Merge two routes and return the updated routes list.
        Based on the original algorithm's join logic.
        """
        p1, p2 = connecting_points
        route1 = routes[route1_idx]
        route2 = routes[route2_idx]
        
        # Get edge positions
        _, pos1 = self.get_edge_insertion_info(p1, route1)
        _, pos2 = self.get_edge_insertion_info(p2, route2)
        
        # Create copies of the paths
        path1 = route1.path.copy()
        path2 = route2.path.copy()
        
        # Determine how to join the routes based on edge positions
        if pos1 == 0 and pos2 == 0:
            # Both points are at the start of their routes
            path1.reverse()
            new_path = path1 + path2
        elif pos1 == 0 and pos2 != 0:
            # p1 at start of route1, p2 at end of route2
            new_path = path2 + path1
        elif pos1 != 0 and pos2 == 0:
            # p1 at end of route1, p2 at start of route2
            new_path = path1 + path2
        else:
            # Both points are at the end of their routes
            path2.reverse()
            new_path = path1 + path2
        
        # Create new merged route
        merged_route = Route(
            path=new_path,
            capacity_used=route1.capacity_used + route2.capacity_used
        )
        
        # Create new routes list without the merged routes
        new_routes = routes.copy()
        
        # Remove routes (remove higher index first to avoid index shifting)
        if route1_idx > route2_idx:
            new_routes.pop(route1_idx)
            new_routes.pop(route2_idx)
        else:
            new_routes.pop(route2_idx)
            new_routes.pop(route1_idx)
        
        # Add the merged route
        new_routes.append(merged_route)
        
        return new_routes
    
    def construct_routes(self, depot: Point, points: List[Point], max_capacity: int = 40) -> List[Route]:
        """
        Main method to construct vehicle routes using Clark-Wright algorithm.
        This closely follows the logic of the original implementation.
        """
        routes: List[Route] = []
        assigned_points: Set[Point] = set()
        
        # Generate savings list (equivalent to distance_saving_ranking)
        savings_list = self.generate_savings_list(depot, points)
        
        for saving_pair in savings_list:
            p1, p2 = saving_pair.point1, saving_pair.point2
            
            # Skip if either point is an interior point (equivalent to original check)
            if self.is_interior_point(p1, routes) or self.is_interior_point(p2, routes):
                continue
            
            # Case 1: Neither point is assigned to any route
            if p1 not in assigned_points and p2 not in assigned_points:
                if p1.demand + p2.demand <= max_capacity:
                    new_route = Route(
                        path=[p1, p2],
                        capacity_used=p1.demand + p2.demand
                    )
                    routes.append(new_route)
                    assigned_points.update([p1, p2])
            
            # Case 2: One or both points are edge points in existing routes
            elif (p1 in assigned_points or p2 in assigned_points):
                routes_with_p1 = self.find_routes_with_edge_point(p1, routes)
                routes_with_p2 = self.find_routes_with_edge_point(p2, routes)
                
                # Case 2a: Only one point is in a route (extend route)
                if len(routes_with_p1) == 1 and len(routes_with_p2) == 0:
                    route_idx = routes_with_p1[0]
                    route = routes[route_idx]
                    
                    # Check if both points are in the same route's edge points
                    if p1 in route.edge_points and p2 in route.edge_points:
                        continue
                    
                    insert_point, insert_pos = self.get_insert_point_and_position((p1, p2), route)
                    
                    if insert_point is not None and route.can_accommodate(insert_point.demand, max_capacity):
                        if insert_pos == 0:
                            route.add_point_at_start(insert_point)
                        else:
                            route.add_point_at_end(insert_point)
                        assigned_points.add(insert_point)
                
                elif len(routes_with_p1) == 0 and len(routes_with_p2) == 1:
                    route_idx = routes_with_p2[0]
                    route = routes[route_idx]
                    
                    # Check if both points are in the same route's edge points
                    if p1 in route.edge_points and p2 in route.edge_points:
                        continue
                    
                    insert_point, insert_pos = self.get_insert_point_and_position((p1, p2), route)
                    
                    if insert_point is not None and route.can_accommodate(insert_point.demand, max_capacity):
                        if insert_pos == 0:
                            route.add_point_at_start(insert_point)
                        else:
                            route.add_point_at_end(insert_point)
                        assigned_points.add(insert_point)
                
                # Case 2b: Both points are in different routes (merge routes)
                elif (len(routes_with_p1) == 1 and len(routes_with_p2) == 1 and 
                      routes_with_p1[0] != routes_with_p2[0]):
                    
                    route1_idx, route2_idx = routes_with_p1[0], routes_with_p2[0]
                    route1, route2 = routes[route1_idx], routes[route2_idx]
                    
                    # Check capacity constraint
                    if route1.capacity_used + route2.capacity_used <= max_capacity:
                        routes = self.merge_routes(routes, route1_idx, route2_idx, (p1, p2))
        
        return routes
    
    def get_total_distance(self, depot: Point, routes: List[Route]) -> float:
        """Calculate the total distance for all routes including depot returns."""
        total_distance = 0.0
        
        for route in routes:
            if route.is_empty:
                continue
            
            # Distance from depot to first point
            total_distance += self.distance_calculator.calculate_distance(depot, route.start_point)
            
            # Distance between consecutive points in the route
            for i in range(len(route.path) - 1):
                total_distance += self.distance_calculator.calculate_distance(
                    route.path[i], route.path[i + 1]
                )
            
            # Distance from last point back to depot
            total_distance += self.distance_calculator.calculate_distance(route.end_point, depot)
        
        return total_distance
    
    def get_route_summary(self, routes: List[Route], depot: Point = None) -> dict:
        """Get a comprehensive summary of the constructed routes."""
        total_capacity = sum(route.capacity_used for route in routes)
        total_distance = self.get_total_distance(depot, routes) if depot else 0.0

        return {
            'num_routes': len(routes),
            'total_capacity_used': total_capacity,
            'total_distance': round(total_distance,2),
            'routes': [
                {
                    'route_id': i,
                    'points': [point.coordinates for point in route.path],
                    'arrival_time': arrive_time_estimator(route, depot),
                    'capacity_used': route.capacity_used,
                    'num_points': len(route.path)
                }
                for i, route in enumerate(routes)
            ]
        }
    
    def validate_solution(self, routes: List[Route], max_capacity: int) -> bool:
        """Validate that the solution meets all constraints."""
        for route in routes:
            if route.capacity_used > max_capacity:
                return False
        return True