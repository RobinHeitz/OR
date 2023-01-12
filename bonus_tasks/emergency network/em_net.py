from gurobipy import Model, GRB, quicksum

AMB = "amb"
HEL = "hel"

# def prepare_data(locations:dict, velocities:dict):
#     from itertools import permutations
#     reaction_times = {}
    
#     amb_vel = velocities.get(AMB)
#     hel_vel = velocities.get(HEL) 

#     for i,j in permutations(locations, 2):
#         loc1 = locations.get(i)
#         loc2 = locations.get(j)
        
#         # euclidian distance: Helicopter
#         d_hel = math.sqrt((loc1[0]-loc2[0])**2 + (loc1[1]-loc2[1])**2)
#         reaction_times[(i,j,HEL)] = round(d_hel / hel_vel, 4)

#         # manhatten distance: Ambulance
#         d_amb = abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1]) # abs(x1-x2) + abs(y1-y2)
#         reaction_times[(i,j,AMB)] = round(d_amb / amb_vel, 4)
#     return reaction_times

def prepare_data(locations:dict, velocities:dict):
    reaction_times = {}
    
    amb_vel = velocities.get("amb")
    hel_vel = velocities.get("hel") 

    for i in locations:
        for j in locations:

            loc1 = locations.get(i)
            loc2 = locations.get(j)
            
            # euclidian distance: Helicopter
            d_hel = ((loc1[0]-loc2[0])**2 + (loc1[1]-loc2[1])**2) ** 0.5
            reaction_times[(i,j,"hel")] = round(d_hel / hel_vel, 4)

            # manhatten distance: Ambulance
            d_amb = abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1]) # abs(x1-x2) + abs(y1-y2)
            reaction_times[(i,j,"amb")] = round(d_amb / amb_vel, 4)
    return reaction_times

    


def solve(transport_methods, locations, locations_hel, capacities, max_supply, velocities):
    reaction_times = prepare_data(
        locations=locations,
        velocities=velocities
    )

    model = Model("emergency_netwORk")

    # x[i,j,t] == 1 if hospital at loc i serves locations j with transport_method t
    x = {}
    
    # y[i,t] == 1 if transport method t is deployed in loc i
    y = {}
    
    max_reaction_time = model.addVar(name=f"MaxReactionTime", vtype=GRB.CONTINUOUS, lb=0)

    
    for i in locations:
        for j in locations:
            for t in transport_methods:
                x[i, j, t] = model.addVar(name=f'x_{i}_{j}_{t}', vtype=GRB.BINARY)
                y[i, t] = model.addVar(name=f'y_{i}_{t}', vtype=GRB.BINARY)

    # If there 
  




    #############
    ### OBJECTIVE 
    #############
    
    model.setObjective(
        max_reaction_time, 
        GRB.MINIMIZE
    )


    ###################
    ### CONSTRAINTS ###
    ###################

    # 0: Linkage of x and y| If there is for some hospital/ deployment location i x[i,j,t]=1  =>  y[i,t] = 1
    # resulting in x could be 0 if y is set, but if x=1 it follows that y=1.
    model.addConstrs(
        x[i,j,t] <= y[i,t] for i in locations for j in locations for t in transport_methods
    )


    # 1: Every loc. needs to be assigned to at least one hospital by at least one transportation method
    model.addConstrs(
        quicksum(x[i,j,t] for i in locations for t in transport_methods) >= 1 for j in locations
    )

    # 2: Helicopters can only deployed in a location if there is also an ambulance deployed.
    model.addConstrs(
        y[i,HEL] <= y[i, AMB] for i in locations
    )

    # 4: Every helicopter can only land in location_hel
    model.addConstrs(
        x[i,j,HEL] == 0 for i in locations for j in locations if j not in locations_hel
    )

    # 5: Helicopters can only be deployed in a hospital if they are able to land there.
    model.addConstrs(
        y[i, HEL] == 0 for i in locations if i not in locations_hel
    )

    # 6: There is a maximum number of deployeable transport methods: (The max for amb is indicating the max of opend hospitals)
    model.addConstrs(
        quicksum(y[i, t] for i in locations) <= max_supply[t] for t in transport_methods
    )

    # 7: The aggregated sum of assignments to a hospital i must be smaller than the available capacity (sum of capacities if heli deployed).
    # Therefore, if we look at heli-locations, there is the sum of capacities (if heli is deployed).
    # Then we look at hospital locations i that are NOT possible heli deployements. There, the capacity is just the ambulance capacity.
    model.addConstrs(
        quicksum(x[i,j,t] for t in transport_methods for j in locations) <= capacities[AMB] + capacities[HEL] * y[i,HEL] for i in locations_hel
    )
    model.addConstrs(
        quicksum(x[i,j,AMB] for j in locations) <= capacities[AMB] for i in locations if i not in locations_hel
    )

    # 9: Set the MaxReactionTime Variable
    model.addConstrs(
        max_reaction_time >= x[i,j,t] * reaction_times[i,j,t] for i,j,t in reaction_times
    )

    # update and optimization. DO NOT change code below this line in your submission
    model.update()
    # model.write('model.lp') # you may comment in this line to see the model in the LP file
    model.optimize()

    return model, x, y, reaction_times



