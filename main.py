import csv
from data.base_locations import STARTING_POSITION
from models.point import Point
from optimizer.clark_wright import ClarkWrightAlgorithm
from distance.euclidean import EuclideanDistanceCalculator

def main():
    #load data from dataset
    points = []

    depot = Point(STARTING_POSITION[0],STARTING_POSITION[1],0)
    total_distance = 0

    with open("data/locations.csv", "r") as file:
        datas = list(csv.reader(file))
        #remove the header 
        datas = datas[1:]
        for row in datas:
            points.append(Point(int(row[0]), int(row[1]), int(row[2])))
    
    algorithm = ClarkWrightAlgorithm(EuclideanDistanceCalculator())
    routes = algorithm.construct_routes(depot, points, max_capacity=40)
    
    # Print results
    summary = algorithm.get_route_summary(routes, depot)
    print(f"Number of routes: {summary['num_routes']}")
    print(f"Total capacity used: {summary['total_capacity_used']}")
    print(f"Total distance cover from all vehicle: {summary['total_distance']}")
    
    for route_info in summary['routes']:
        print(f"Route {route_info['route_id']}: {route_info['points']} "
              f"(Capacity: {route_info['capacity_used']})")
    

            



if __name__=="__main__":
    main()