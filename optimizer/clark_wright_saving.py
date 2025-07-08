import copy
from .route_utils import get_euclidean_distance
import itertools

class Clark_Wright_Saving_Algorithm:

    def distance_saving_algo(self, depot:tuple[int,int], p1:tuple[int,int], p2:tuple[int,int]):
        saved_distance = get_euclidean_distance(depot,p1)+get_euclidean_distance(depot,p2)-get_euclidean_distance(p1,p2)
        return saved_distance
    
    def distance_saving_ranking(self, depot:tuple, points:list[tuple[int,int]]):
        depot_points_comb = list(itertools.combinations(points,2))
        saved_distance_dict = {}

        for i in depot_points_comb:
            saved_distance = self.distance_saving_algo(depot,i[0],i[1])
            saved_distance_dict[i] = saved_distance
        saved_distance_dict = dict(sorted(saved_distance_dict.items(), key=lambda item:item[1], reverse=True))
        return saved_distance_dict
    
    def find_edge_points(self, routes:list[dict]):
        edge_points = []
        for route in routes:
            if len(route['path']) < 1:
                edge_points.append([])
            elif len(route['path']) == 1:
                edge_points.append([route['path'][0]])
            else:
                edge_points.append([route['path'][0], route['path'][-1]])
        return edge_points

    def find_route_edge_points_index(self, points:tuple[int,int], edge_points_list:list[list[tuple[int,int]]]):
        edge_points_index = set()
        for index, edge_points in enumerate(edge_points_list):
            if points[0] in edge_points or points[1] in edge_points:
                edge_points_index.add(index)
        return list(sorted(edge_points_index))
        
    def find_interior_points(self, routes:list[dict]):
        interior_points_route = []
        for route in routes:
            if len(route['path'])<=2:
                continue
            else:
                route['path'].pop(0)
                route['path'].pop(-1)
                interior_points_route.append(route['path'])
        return interior_points_route

    def insert_point_and_edge_point_index(self, points:tuple[int,int], route_path:list[tuple[int,int]]):
        edge_point = None
        insert_point = None
        edge_index = None
        if points[0] in route_path:
            edge_point = points[0]
            insert_point = points[1]
            edge_index = 0 if route_path[0] == edge_point else len(route_path) - 1
        elif points[1] in route_path:
            edge_point = points[1]
            insert_point = points[0]
            edge_index = 0 if route_path[0] == edge_point else len(route_path) - 1
        return insert_point, edge_index
        
    def vehicles_route_construct(self, saved_distance_dict:dict[tuple,float], locations:dict[tuple,int], depot:tuple[int,int], capacity=40):
            routes = []
            points_with_route = set()
            for points in list(saved_distance_dict.keys()):

                edge_points_list = self.find_edge_points(copy.deepcopy(routes))
                interior_points_list = self.find_interior_points(copy.deepcopy(routes))

                if any(points[0] in sublist for sublist in interior_points_list) or any(points[1] in sublist for sublist in interior_points_list):
                    continue

                elif points[0] not in points_with_route and points[1] not in points_with_route:
                    routes.append({'path':[points[0],points[1]], 'capacity':locations[points[0]]+locations[points[1]]})
                    points_with_route.add(points[0])
                    points_with_route.add(points[1])

                elif any(points[0] in sublist for sublist in edge_points_list) or any(points[1] in sublist for sublist in edge_points_list):
                    edge_points_index_set = self.find_route_edge_points_index(points, edge_points_list)
                    if len(edge_points_index_set) == 1:
                        new_routes = copy.deepcopy(routes)
                        if any(points[0] in sublist for sublist in edge_points_list) and any(points[1] in sublist for sublist in edge_points_list):
                            continue

                        insert_point, edge_index = self.insert_point_and_edge_point_index(points, routes[edge_points_index_set[0]]['path'].copy())

                        if insert_point is None or edge_index is None:
                            continue
                        if edge_index == 0 and new_routes[edge_points_index_set[0]]['capacity'] + locations[insert_point] <= capacity:
                            new_routes[edge_points_index_set[0]]['path'].insert(0, insert_point)

                        elif edge_index != 0 and new_routes[edge_points_index_set[0]]['capacity'] + locations[insert_point] <= capacity:
                            new_routes[edge_points_index_set[0]]['path'].append(insert_point)
                        else:
                            continue

                        new_routes[edge_points_index_set[0]]['capacity'] += locations[insert_point]
                        points_with_route.add(insert_point)

                        routes = new_routes

                    elif len(edge_points_index_set) == 2:
                        if routes[edge_points_index_set[0]]['capacity'] + routes[edge_points_index_set[1]]['capacity'] <= capacity:
                            insert_point1, edge_index1 = self.insert_point_and_edge_point_index(points, routes[edge_points_index_set[0]]['path'].copy())
                            insert_point2, edge_index2 = self.insert_point_and_edge_point_index(points, routes[edge_points_index_set[1]]['path'].copy())

                            new_routes = copy.deepcopy(routes)
                            new_route_current_capacity = new_routes[edge_points_index_set[0]]['capacity'] + new_routes[edge_points_index_set[1]]['capacity']
                            join_route = None
                            match (edge_index1, edge_index2):
                                case (0,0):
                                    new_routes[edge_points_index_set[0]]['path'].reverse()
                                    join_route = new_routes[edge_points_index_set[0]]['path'] + new_routes[edge_points_index_set[1]]['path']
                                case (0,_):
                                    join_route = new_routes[edge_points_index_set[1]]['path'] + new_routes[edge_points_index_set[0]]['path']
                                case (_,0):
                                    join_route = new_routes[edge_points_index_set[0]]['path'] + new_routes[edge_points_index_set[1]]['path']
                        
                                case (_,_):
                                    new_routes[edge_points_index_set[1]]['path'].reverse()
                                    join_route = new_routes[edge_points_index_set[0]]['path'] + new_routes[edge_points_index_set[1]]['path']

                        
                            new_routes.pop(edge_points_index_set[1])

                            new_routes.pop(edge_points_index_set[0])

                            new_routes.append({'path': join_route, 'capacity':new_route_current_capacity})

                            routes = new_routes

            return routes


        
