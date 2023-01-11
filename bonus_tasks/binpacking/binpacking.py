from gurobipy import Model, GRB, quicksum


def solve(items, bins, conflicts, capacity, weight):
    # Model
    model = Model("Binpacking with conflicts")

    # Decision variable x_i_j indicates whether Item i is packed into Bin j (value 1) or not (value 0).
    x = {}
    for i in items:
        for j in bins:
            # TODO: Adjust additional attributes (lb, ub, vtype, obj). Do NOT change the name!
            x[i, j] = model.addVar(name=f'x_{i}_{j}', vtype=GRB.BINARY)
    

    # Decision variable y_j indicates whether Bin j is used (value = 1) or not (value = 0).
    y = {}
    for j in bins:
        # TODO: Adjust additional attributes (lb, ub, vtype, obj). Do NOT change the name!
        y[j] = model.addVar(name=f'y_{j}', vtype=GRB.BINARY)

    
    model.setObjective(
        quicksum(y[j] for j in bins),
        GRB.MINIMIZE
    )


    # Coupling of variables
    model.addConstrs(
        x[i,j] <= y[j] for i in items for j in bins
    )          
    
    # every item should be placed in a bin
    model.addConstrs(
        quicksum(x[i,j] for j in bins) == 1 for i in items
    )          

    # capacity constraints
    model.addConstrs(
        quicksum(x[i,j] * weight[i] for i in items) <= capacity for j in bins
    )

    # Conflicts
    model.addConstrs(
        x[i,j] + x[k,j] <= 1 for i,k in conflicts for j in bins
    )





    # Update and Solve
    model.update()
    model.optimize()

    # Return the model: Do not change/remove this line - it is crucial for our scoring method
    # and removal may lead to a score of 0!
    return model

