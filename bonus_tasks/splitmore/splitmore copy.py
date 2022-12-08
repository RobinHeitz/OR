from gurobipy import quicksum, GRB, Model


def prepare_data(groups, payment_methods):
    # build list of all people and dictionary of their net balances
    people = []
    balances = {}
    for group in groups:
        for person in group:
            if person not in people:
                people.append(person)
                balances[person] = group[person]
            else:
                balances[person] = balances[person] + group[person]

    # build dictionaries for looking up friends and a dictionary for shared methods between friends
    friends = {p: [] for p in people}
    shared_methods = {}
    for person in friends:
        for group in groups:
            if person in group:
                for pot_friend in group:
                    if not pot_friend == person:
                        if pot_friend not in friends[person]:
                            friends[person].append(pot_friend)
                            shared_methods[(person,pot_friend)] = [m for m in payment_methods[person] if m in
                                                                   payment_methods[pot_friend]]
    return people, friends, balances, shared_methods


def solve(groups, max_transactions_pp, payment_methods):
    # retrieve converted data
    people, friends, balances, shared_methods = prepare_data(groups, payment_methods)


    # define parameter C[p1, p2] as the maximum absolute value of the balances of the respective trading partners p1 and p2
    # c[p1, p2] = max {|bp1|, |bp2|} for all p1€P and p2€Fp1
    c = {}
    for p1 in people:
        for p2 in friends[p1]:
            c[p1, p2] = max( abs(net_balance) for net_balance in (balances[p1], balances[p2]))


    model = Model("splitmORe")

    #################
    # setup variables
    #################

    # x >= 0: Amount a person p1 transacts to p2 with given method m
    x = {}
    for p1 in people:
        for p2 in friends[p1]:
            for m in shared_methods[p1, p2]:
                x[p1, p2, m] = model.addVar(name=f'x_{p1}_{p2}_{m}', vtype=GRB.CONTINUOUS, lb=0) 

    # y = 1 if there is a transaction between p1, p2 with method m. Needed to min. the amount of transactions
    y = {}
    for p1 in people:
        for p2 in friends[p1]:
            for m in shared_methods[p1, p2]:
                y[p1, p2, m] = model.addVar(name=f'y_{p1}_{p2}_{m}', vtype=GRB.BINARY) 

    # introduce binary variable Z that declares (zp = 1) if a person should receive money <=> that persons net balance is positive
    z = {}
    for p in people:
        z[p] = model.addVar(name=f"z_{p}", vtype=GRB.BINARY)


    #############
    # Objective #
    #############

    model.setObjective(
        quicksum(y[p1, p2, m] for p1 in people for p2 in friends[p1] for m in shared_methods[p1, p2]), 
        GRB.MINIMIZE
    )

    ###############
    # Constraints #
    ###############

    # if a person has a positive balance (zp = 1), than the sum of receiving payments over all methods m must equals the (positive) balance of that person.
    model.addConstrs(
        z[p2] * balances[p2] == quicksum(x[p1, p2, m] for p1 in friends[p2] for m in shared_methods[p1, p2]) for p2 in people
    )

    # the total used payment methods for 2 partners should be at most 1.
    model.addConstrs(
        quicksum(y[p1, p2, m] for m in shared_methods[p1, p2]) <= 1 for p1 in people for p2 in friends[p1]
    )

    # the total number of transactions for a person must be lower than/ equal to max_transactions_pp
    model.addConstrs(
        quicksum(y[p1, p2, m] for p2 in friends[p1] for m in shared_methods[p1, p2]) <= max_transactions_pp for p1 in people
    )

    # Set Zp = 1 if the person p has positive balance, thus should receive money.
    model.addConstrs(
        z[p] * 1_000_000_000 >= balances[p] for p in people
    )



    # coupling of z and x: If x > 0 (meaning p1 sends p2 money), than p2 has a positive balance (thus, z_ps = 1).
    # model.addConstrs(
    #     x[p1, p2, m] <= z[p2] * 1_000_000_000_000_000 for p1 in people for p2 in friends[p1] for m in shared_methods[p1, p2]
    # )

    # coupling of y and x: if y = 0 => x = 0, otherwise if x > 0 then there is a transaction between p1, p2 thus resulting in yp1, p2 = 1
    model.addConstrs(
        1_000_000_000_000_000 * y[p1, p2, m] >= x[p1, p2, m] for p1 in people for p2 in friends[p1] for m in shared_methods[p1, p2]
    )

    # a transaction amount between p1, p2 is at most the max of (absolute) balances of p1, p2
    model.addConstrs(
        x[p1, p2, m] <= c[p1, p2] for p1 in people for p2 in friends[p1] for m in shared_methods[p1, p2]
    )


    # update and optimization. DO NOT change code below this line in your submission
    model.update()
    # model.write('model.lp')
    model.optimize()

    # print solution
    if model.status == GRB.OPTIMAL:
        print(f'\nObjective: {model.ObjVal}\n')
        print(f'\n====== Balances =====')
        for p in people:
            print(f'{p} is at {round(balances[p],2)}')
        print('\n====== Flow =====')
        for p1 in people:
            for p2 in friends[p1]:
                if len(shared_methods[(p1, p2)]) > 0:
                    for m in shared_methods[(p1, p2)]:
                        if round(x[p1, p2, m].x,2) > 0:
                            print(f'{p1} gives {p2} {round(x[p1, p2, m].x,2)} EUR via {m}')

    return model

