import math
from datetime import datetime, timedelta
from typing import List
from models.point import Point
from models.route import Route

def get_euclidean_distance(start:Point, target:Point) -> float:
    distance = round(math.sqrt(abs(target.x-start.x)**2 + abs(target.y-start.y)**2),2)
    return distance

def arrive_time_estimator(route:Route, depot:Point, vehicle_speed=20):
    route_with_arrival_time_dict = {}
    current_time = datetime.now()
    path = route.path

    for i in range(len(path)):
        distance = 0
        if i==0 or i==len(path)-1:
            distance = get_euclidean_distance(depot, path[i])
        else:
            distance = get_euclidean_distance(path[i-1],path[i])

        estimated_time = distance / vehicle_speed
        current_time = current_time + timedelta(minutes=estimated_time)
        route_with_arrival_time_dict[path[i].coordinates] = current_time.strftime('%Y-%m-%d %H:%M:%S')

    return route_with_arrival_time_dict