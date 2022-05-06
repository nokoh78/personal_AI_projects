import time
import queue
import random
import copy
import concurrent.futures

class Cars:
    def __init__(self, length, route):
        self.length = length
        self.route = route
        self.which_street = 0
        self.to_end_of_street = 1

    def get_street(self):
        return self.route[self.which_street]

    def get_no_intersection(self, streets):
        return streets[self.get_street()][2]

class Intersection:
    def __init__(self):
        self.time = 0
        self.schedule = []
        self.schedule_seconds = []

def starting_solution(file_name, data=False):
    f = open(file_name, "r")

    simulation_data = f.readline().split()
    duration = int(simulation_data[0])
    no_streets = int(simulation_data[2])
    no_cars = int(simulation_data[3])
    score = int(simulation_data[4])

    streets = {}  # key: name of the street; value: (time, starting intersection, ending intersection)
    intersections = {}  # key: name of the intersection; value: list of streets names
    streets_activity = {}  # key: name of the street; value: number of times the street is used
    final = {}  # key: name of the intersection; value: a list of tuples (name of the street, scheduled green light for that street)
    cars2 = []

    for i in range(no_streets):
        temp = f.readline().split()
        streets[temp[2]] = (int(temp[3]), int(temp[0]), int(temp[1]))

    for street in streets:
        streets_activity[street] = 0

    cars = []
    for i in range(no_cars):
        temp = f.readline().split()
        cars.append(temp[1:])
        cars2.append(Cars(int(temp[0]) - 1, tuple(temp[1:])))
    f.close()

    for car in cars:
        for street in car:
            streets_activity[street] += 1

    for street in streets_activity:
        if streets_activity[street] != 0:
            if streets[street][2] in intersections.keys():
                intersections[streets[street][2]].append(street)
            else:
                intersections[streets[street][2]] = [street]


    for inters in intersections:
        final[inters] = Intersection()
        for street in intersections[inters]:
            final[inters].schedule.append(street)
            final[inters].time += 1
            final[inters].schedule_seconds.append([street, 1])

    #for i in final:
    #   print(final[i].time, final[i].schedule_seconds, final[i].schedule)
    if data is True:
        return final, streets, cars2, score, duration

def simulation(schedule, streets, carsto, score, duration):

    final_score = 0
    intersections = {}
    cars = copy.deepcopy(carsto)
    for second in range(duration):
        # print(second, 'second')
        for car in cars[:]:
            car.to_end_of_street -= 1

            if car.to_end_of_street == 0:

                if car.which_street == car.length:
                    final_score += score
                    final_score += (duration - 1 - second)
                    # print(duration - 1 - second, 'score')
                    # print(car.route)
                    cars.remove(car)

                else:
                    intersection = car.get_no_intersection(streets)
                    street = car.get_street()

                    if intersection in intersections.keys() and street in intersections[intersection].keys():
                        intersections[intersection][street].put(car)
                    elif intersection in intersections.keys():
                        intersections[intersection][street] = queue.Queue()
                        intersections[intersection][street].put(car)
                    else:
                        intersections[intersection] = {street: queue.Queue()}
                        intersections[intersection][street].put(car)
                    # put car to the intersection
                    car.to_end_of_street -= 1

        # after this part all cars has been moved on their streets or  put on their intersections
        # next session will execute schedule

        for intersection in list(intersections.keys()):
            green = schedule[intersection].schedule[second % schedule[intersection].time]  # awesome line of code
            # print(green)
            if green in intersections[intersection].keys():
                car = intersections[intersection][green].get()
                if len(intersections[intersection][green].queue) == 0:
                    del intersections[intersection][green]
                car.which_street += 1
                # print(car.which_street, "which")
                # print(car.get_street())
                car.to_end_of_street = streets[car.get_street()][0]
                # print(car.to_end_of_street)
                if not intersections[intersection]:
                    del intersections[intersection]
    #print(final_score)
    return final_score

def mutation(schedule_org, mutation_probability):
    schedule = copy.deepcopy(schedule_org)
    for intersection in schedule:
        if len(schedule[intersection].schedule_seconds) > 1 and   random.random() < mutation_probability :
            if random.random() < 0.15 :
                street = random.choice(schedule[intersection].schedule_seconds)
                if random.random() < 0.5 :
                    if len(schedule[intersection].schedule) > 1:
                        if  street[1] > 0:
                            street[1] -= 1
                            schedule[intersection].schedule.remove(street[0])
                            schedule[intersection].time -= 1
                else:
                    if street[1] == 0:
                        schedule[intersection].schedule.append(street[0])
                    else :
                        schedule[intersection].schedule.insert( schedule[intersection].schedule.index(street[0]), street[0])
                    street[1] += 1
                    schedule[intersection].time += 1

            else:
                first = random.randint(0, len(schedule[intersection].schedule_seconds)-1)
                second = random.randint(0, len(schedule[intersection].schedule_seconds)-1)
                schedule[intersection].schedule_seconds[first], schedule[intersection].schedule_seconds[second] = schedule[intersection].schedule_seconds[second], schedule[intersection].schedule_seconds[first]
                schedule[intersection].schedule = []
                for street in schedule[intersection].schedule_seconds:
                    schedule[intersection].schedule += [street[0] for duration in range(street[1])]
            #print(schedule[intersection].schedule_seconds)
            #print(schedule[intersection].schedule)

    return schedule

def crossover(parent1, parent2):
    child = {}
    for intersection in parent1:
        if random.random() < 0.5:
            child[intersection] = copy.deepcopy(parent1[intersection])
        else:
            child[intersection] = copy.deepcopy(parent2[intersection])
    return child

def getTournamentSelection(populationSize, size):
    l = [random.randint(0, populationSize - 1) for i in range(size)]
    return min(l)

def getParentIndices(populationSize, K):
    return (getTournamentSelection(populationSize, size=K), getTournamentSelection(populationSize, size=K))

def get_child (population, population_size, mutation_probability, tournament_size, streets, cars, score, duration):
    parent1, parent2 = getParentIndices(population_size, tournament_size)
    child = mutation(crossover(population[parent1][1], population[parent2][1]), mutation_probability)
    return [simulation(child, streets, cars, score, duration), child]

def getOffspring (population, population_size, mutation_probability, tournament_size, streets, cars, score, duration):

    #result = []
    #for i in range(population_size):
    #    result.append(get_child(population, population_size, mutation_probability, tournament_size, streets, cars, score, duration))
    #return result
    off_spring = [concurrent.futures.ProcessPoolExecutor().submit(get_child, population, population_size, mutation_probability, tournament_size, streets, cars, score, duration) for i in range(population_size)]
    results = [f.result() for f in concurrent.futures.as_completed(off_spring) ]
    return results

def print_schedule(best_schedule):

    print(len(best_schedule))
    for intersection in best_schedule:
        print(intersection)
        print( len(best_schedule[intersection].schedule_seconds))
        for street in best_schedule[intersection].schedule_seconds:
            print(street[0] , street[1])

def main(filename):

    start = time.time()
    mutation_probability = 0.008
    tournament_size = 2

    starting_schedule, streets, cars, score, duration = starting_solution(filename, data=True)

    timer = time.time()
    starting_fitness = simulation(starting_schedule, streets, cars, score, duration)
    how_long = time.time() - timer
    if   how_long > 1: population_size = 15
    elif how_long > 2: population_size = 16
    elif how_long > 1: population_size = 18
    elif how_long > 0.5: population_size = 25
    else:            population_size = 40

    best_score = starting_fitness
    best_schedule = starting_schedule

    population = [[starting_fitness, starting_schedule] for schedule in range(population_size)]

    while time.time() - start < 285:
    #for i in range(20):
        #print(time.time() - start)
        offSpring  = getOffspring(population, population_size, mutation_probability, tournament_size, streets, cars, score, duration)
        parents_and_children = population + offSpring
        parents_and_children.sort(key=lambda x: x[0], reverse = True)

        survivors = []
        for i in range(population_size):
            if random.random() < 0.3:
                survivorIDX = (getTournamentSelection(population_size, 2))
            else : survivorIDX = (getTournamentSelection(population_size, 1))
            survivors.append(parents_and_children[survivorIDX])
        population = survivors
        population.sort(key=lambda x: x[0], reverse = True)


        #print(population[0][0])
        if population[0][0] > best_score:
            best_score = population[0][0]
            best_schedule = population[0][1]

    #print(best_score)
    print_schedule(best_schedule)


if __name__ == "__main__":
    main("a.txt")


