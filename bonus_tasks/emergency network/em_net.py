from gurobipy import *


def prepare_data(locations, velocities):
    reaction_times = {}
    # TODO: Calculate reaction times for ambulances and helicopters. Hint: the visualization function expects
    # TODO: the format: reaction_times[i, j, t]
    return reaction_times


def solve(transport_methods, locations, locations_hel, capacities, max_supply, velocities):
    # calculate reaction times  # TODO: Calculate reaction times within the function above
    reaction_times = prepare_data(
        locations=locations,
        velocities=velocities
    )

    model = Model("emergency_netwORk")

    # variables
    x = {}
    y = {}
    for ...:
        # TODO: Implement a logic to define the variables x and y. Add attributes where needed. DO NOT change the name
        x[i, j, t] = model.addVar(name=f'x_{i}_{j}_{t}')
        y[i, t] = model.addVar(name=f'y_{i}_{t}')

    # TODO: Add additional variables if needed for your model

    # constraints
    # TODO: Add your constraints below

    # objective function
    # TODO Add your objective function here (or do that with the variable definition)

    # update and optimization. DO NOT change code below this line in your submission
    model.update()
    # model.write('model.lp') # you may comment in this line to see the model in the LP file
    model.optimize()

    return model, x, y, reaction_times



