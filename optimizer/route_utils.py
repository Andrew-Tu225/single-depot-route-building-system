import math
from datetime import datetime, timedelta
from data.base_locations import STARTING_POSITION


def get_euclidean_distance(start:tuple, target:tuple) -> float:
    distance = round(math.sqrt(abs(target[0]-start[0])**2 + abs(target[1]-start[1])**2),2)
    return distance

def arrive_time_estimator(route:list, vehicle_speed=20):
    route_with_arrival_time_dict = {}
    current_time = datetime.now()
    for i in range(len(route)):
        distance = 0
        if i==0 or i==len(route)-1:
            distance = get_euclidean_distance(STARTING_POSITION, route[i])
        else:
            distance = get_euclidean_distance(route[i-1],route[i])

        estimated_time = distance / vehicle_speed
        current_time = current_time + timedelta(minutes=estimated_time)
        route_with_arrival_time_dict[route[i]] = current_time.strftime('%Y-%m-%d %H:%M:%S')

    return route_with_arrival_time_dict
            
