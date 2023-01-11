from gurobipy import GRB, Model, quicksum


model = Model("Testing stuff")

people = ("Anna", "Boris", "Chantal", "Doris", "Uwe", "Mathias")
balances_amount = [val * (-1)**i for i, val in enumerate((9,4,7,1,8,11))]

balances = {}

for index, p in enumerate(people):
    balances[p] = balances_amount[index]


print(balances)

z = {}
for p in people:
    z[p] = model.addVar(name=f"z_{p}", vtype=GRB.BINARY)


model.addConstrs(
    balances[p] <= z[p] * 100 for p in people
)

model.setObjective(
    quicksum(z[p] for p in people)
)

model.update()
model.optimize()

for p in people:
    print(f"{p:12} | balance: {balances[p]:4} | {z[p].X}")