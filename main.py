import csv
from optimizer.clark_wright_saving import Clark_Wright_Saving_Algorithm
from data.base_locations import STARTING_POSITION
from optimizer.route_utils import arrive_time_estimator,get_route_distance


def main():
    #load data from dataset
    locations = {}

    total_distance = 0

    with open("data/locations.csv", "r") as file:
        datas = list(csv.reader(file))
        #remove the header 
        datas = datas[1:]
        for row in datas:
            locations[(int(row[0]),int(row[1]))] = int(row[2])

    
    Saving_Algorithm = Clark_Wright_Saving_Algorithm()
    saved_distance_dict = Saving_Algorithm.distance_saving_ranking(STARTING_POSITION, list(locations.keys()))
    routes = Saving_Algorithm.vehicles_route_construct(saved_distance_dict, locations, STARTING_POSITION, 45)

    vehicle_index = 1
    for route in routes:
        total_distance += get_route_distance(route['path'])
        print(f"vehicle {vehicle_index}: ", arrive_time_estimator(route['path']))
        vehicle_index += 1

    print(f"total distance cover by from all routes: {total_distance}")
            



if __name__=="__main__":
    main()