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

    big_M = 1_000_000_000_000

    # define parameter C[p1, p2] as the maximum absolute value of the balances of the respective trading partners p1 and p2
    # c[p1, p2] = max {|bp1|, |bp2|} for all p1€P and p2€Fp1
    c = {}
    for p1 in people:
        for p2 in friends[p1]:
            c[p1, p2] = max( abs(balances[p1]), abs(balances[p2]))

    print("Our defined parameter C_p1_p2 (max. value of the |b_p|'s of the respective trading partners p1, p2")
    for k in c.keys():
        print(f"{str(k):25} | {c[k]}")


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

    # Set Zp to 1 if the person p has positive net balance, meaning p should receive funds.
    # model.addConstrs(
    #     balances[p] <= big_M * z[p] for p in people
    # )

    for p in people:
        
        print(f"P = {p:13} and balance is: {balances[p]}")
        
        model.addConstr(
            balances[p] <= 9999999999* z[p]
        )

  



    # # if x > 0 => Y = 1, meaning htat p1 sends p2 money. M >= max absolute value of net balances of the two respective transaction partners
    # # for not calculating arbitrary M_y's for any pair of transaction partners, we define M as max of all net balances, thus making it equal to M_z
    # # M_y = M_z
    # model.addConstrs(
    #     big_M * y[p1, p2, m] >= x[p1, p2, m] for p1 in people for p2 in friends[p1] for m in shared_methods[p1, p2]
    # )


    # # if a person p2 has positive balance (z_p2 = 1), that means that all receiving funds from any person to p2 must sum up tp b_p2.
    # model.addConstrs(
    #     z[p2] * balances[p2] == quicksum(x[p1, p2, m] for p1 in friends[p2] for m in shared_methods[p1, p2]) for p2 in people
    # )


    # # between 2 people p1, p2 at most one method of payments can be used.
    # model.addConstrs(
    #     quicksum(y[p1, p2, m] for m in shared_methods[p1, p2]) <= 1 for p1 in people for p2 in friends[p1]
    # )

    # # a single person must not make more than max_transactions_pp transactions
    # model.addConstrs(
    #     quicksum(y[p1, p2, m] for p2 in friends[p1] for m in shared_methods[p1, p2]) <= max_transactions_pp for p1 in people
    # )


    # # A transaction must not be higher than max{ |b_p1|, |b_p2|}. Parameter c[p1, p2] pre-computes this term.
    # model.addConstrs(
    #     x[p1, p2, m] <= c[p1, p2] for p1 in people for p2 in friends[p1] for m in shared_methods[p1, p2]
    # )







    # update and optimization. DO NOT change code below this line in your submission
    model.update()
    # model.write('model.lp')
    model.optimize()

    # print solution
    if model.status == GRB.OPTIMAL:
        print(f'\nObjective: {model.ObjVal}\n')
        print(f'\n====== Balances =====')
        for p in people:
            print(f'{p} is at {round(balances[p],2)} and Z is {z[p].X}')
        print('\n====== Flow =====')
        for p1 in people:
            for p2 in friends[p1]:
                if len(shared_methods[(p1, p2)]) > 0:
                    for m in shared_methods[(p1, p2)]:
                        if round(x[p1, p2, m].x,2) > 0:
                            print(f'{p1} gives {p2} {round(x[p1, p2, m].x,2)} EUR via {m}')

        # print(f'\n====== Variable Z - if z=1 => p€people should receive funds. =====')
        # for p in people:
        #     print(f"{people:20} | ")
        
        
        
        print(f'\n====== Balances after processed transactions: =====')
        for p1 in people:
            incoming = quicksum(x[p2, p1, m].X for p2 in friends[p1] for m in shared_methods[p1, p2]).getValue()
            outgoing = quicksum(x[p1, p2, m].X for p2 in friends[p1] for m in shared_methods[p1, p2]).getValue()
            print(f"{p1} is at {balances[p1] - incoming + outgoing}")




    return model

