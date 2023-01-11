from gurobipy import *
from gurobipy import Model, quicksum, GRB

def solve(stands,
          temperature,
          amount,
          alcohol_content,
          sugar,
          calorific_value,
          price,
          cup_type,
          people,
          budget,
          min_wine_total,
          max_wine_per_stand,
          min_avg_temperature):

    model = Model("christmas_market")

    # variable x
    x = {}
    for p in people:
        for s in stands:
            # modify vtype, lb, ub, obj. DO NOT change the name attribute, this is a requirement of tutOR.
            x[p, s] = model.addVar(name=f'x_{p}_{s}', vtype = GRB.INTEGER, lb=0)



    # Variables C_min, c_max represents the min and max amount of wines drunk from one person (at every stand s)
    c_min, c_max = {},{}
    for s in stands:
        c_min[s] = model.addVar(name=f"c_min_{s}", vtype=GRB.INTEGER, lb=0)
        c_max[s] = model.addVar(name=f"c_max_{s}", vtype=GRB.INTEGER, lb=0)
    

    # min total costs
    model.setObjective(
        quicksum(price[s] * x[p,s] for s in stands for p in people)
    )

    model.update()  # update to make the variables known


    # budget
    model.addConstrs(
        quicksum(price[s] * x[p,s] for s in stands) <= budget[p] for p in people
    )

    # max_wine_per_stand:
    model.addConstrs(
        max_wine_per_stand[p,s] >= x[p,s] for p in people for s in stands
    )

    # min_wine_total
    model.addConstrs(
        quicksum(x[p,s] for s in stands) >= min_wine_total[p] for p in people
    )


    # avg drinking temperature
    model.addConstrs(
        quicksum(x[p,s] * amount[s] * temperature[s] for s in stands) >= min_avg_temperature * quicksum(x[p,s] * amount[s] for s in stands) for p in people
    )

    # no one is waiting to long for another person
    model.addConstrs(
        c_max[s] - c_min[s] <= 1 for s in stands
    )

    # coupling of c_max with xp,s
    model.addConstrs(
        c_max[s] >= x[p,s] for s in stands for p in people
    )

    # coupling of c_min with xp,s
    model.addConstrs(
        c_min[s] <= x[p,s] for s in stands for p in people
    )

    # update and optimization. DO NOT change code below this line in your submission
    model.update()
    model.optimize()

    for s in stands:
        print(f"C_max_{s} = {c_max[s].X}")
        print(f"C_min_{s} = {c_min[s].X}")


    # print solution
    if model.status == GRB.OPTIMAL:
        print(f'\n objective: {model.ObjVal}\n')
        for p in people:
            for s in stands:
                if int(x[p, s].x) >= 1:
                    print(f'{p} drinks {int(x[p, s].x)} cups at {s}')

    return model
