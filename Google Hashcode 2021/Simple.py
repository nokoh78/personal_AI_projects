import math
import time
import random

def simple_solution(file_name, schedule=False):
    f = open(file_name, "r")  # opening a file with all the information regarding the simulation

    # reading the first line from the input file and creating variables out of that data
    simulation_data = f.readline().split()
    duration = int(simulation_data[0])
    no_intersections = int(simulation_data[1])
    no_streets = int(simulation_data[2])
    no_cars = int(simulation_data[3])
    score = int(simulation_data[4])

    streets = {}  # key: name of the street; value: (time, starting intersection, ending intersection)
    intersections = {}  # key: name of the intersection; value: list of streets names
    streets_activity = {}  # key: name of the street; value: number of times the street is used
    final = {}  # key: name of the intersection; value: a list of tuples (name of the street, scheduled green light for that street)

    # we iterate through all the streets written in the input file and copy names of the streets into a dictionary named "streets"
    for i in range(no_streets):
        temp = f.readline().split()
        streets[temp[2]] = (
        int(temp[3]), int(temp[0]), int(temp[1]))  # streets[key] = (time, starting intersection, ending intersection)

    # we create all of the keys in a dictionary "streets_activity" and the activity for every street, for now, is set to 0, to make it easier
    # to update that value later in the code
    for street in streets:
        streets_activity[street] = 0

    cars = []  # cars is a list of paths that each car is taking
    # we iterate through all the lines in the input file that contain the information about cars and we append each car's path to a list named "cars"
    for i in range(no_cars):
        temp = f.readline().split()
        cars.append(temp[1:])  # we discard the element with an index 0, because it contains information about a number of streets, which we do not need

    f.close()  # we have read all the information that we need from the file, so we can close it

    # we iterate through each path in a list "cars" and add 1 to a total activity (a value in a dictionary "streets")
    # of a street (which is a key in a dictionary "streets") to count the number of times the street appears in all cars' paths
    for car in cars:
        for street in car:
            streets_activity[street] += 1

    # we iterate through each street in the dictionary "streets_activity" but we imediately discard those streets that are never used by any cars, because
    # we do not need to be included in a schedule
    # we take an ending intersection from a dictionary "streets" and we check whether it is already in a dictionary "intersections"
    # if it is, we append a name of a street into a list that is a value of a certain key and contains name of every street that ends at this interseection
    # if no, we create a new key in a dictionary "intersections" and assign it a list with a certain street as a value
    for street in streets_activity:
        if streets_activity[street] != 0:
            if streets[street][2] in intersections.keys():
                intersections[streets[street][2]].append(street)
            else:
                intersections[streets[street][2]] = [street]

    # we iterate through all the names of the intersections in the dictionary "intersections"
    # we create a key in the dictionary "final" that is, for now, an empty list
    # we set a minimal activity for each intersection as infinity, because we want to make sure, that it is the biggest possible value
    # we iterate through all the streets that are ending at a certain intersection
    # we check if the activity on that street is the smallest of all the previous ones, if yes-> we update a min value to this activity

    # we again iterate through all the streets that are ending their path at a certain intersection
    # we normalize the activity on each street on that intersection, so that we can create schedule for how long a green light will light on that street
    # (we use a minimal activity counted in a loop above)
    # finally, we append a tuple with (name of a street, how long this street will have a green light) to a dictionary "final"
    # with a key = name of the intersection that the street ends at
    for intersection in intersections:
        final[intersection] = []
        min = math.inf
        for street in intersections[intersection]:
            if streets_activity[street] < min:
                min = streets_activity[street]

        for street in intersections[intersection]:
            activity = round(streets_activity[street] / min)
            final[intersection].append((street, activity))

    # we iterate through all he keys in a dictionary "final"
    # we check if the length of a list of streets and its green light's time is bigger than 1, because those streets will be sorted
    # if yes-> we sort each list so that the elements with a longer time of a scheduled green light will be first, because we want to prioritize them
    # to make sure, the streets "used by" the most cars will have green light for the longest time (schedule reads from the first element on it to the last)
    for key in final:
        if len(final[key]) > 1:
            final[key] = sorted(final[key], key=lambda i: i[1], reverse=True)

    print(str(len(intersections)))  # we write a number of intersections that are being used in our simulation

    # we iterate through the intersections (keys) in the dictionary "final" and write the name of earch intersection and the number of streets for which
    # we created a schedule
    # we iterate through all the streets that end their paths in this intersection and write a name of each street and its activity
    for intersection in final:
        print(str(intersection))
        print(str(len(final[intersection])))
        for street in final[intersection]:
            print(street[0], str(activity))

    if schedule is True:
        return final

start_time = time.time()  # starting the counting
simple_solution("f.txt", schedule=True)
#print(time.time() - start_time)  # we count the time that it took for the program to work