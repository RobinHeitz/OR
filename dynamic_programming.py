import numpy as np


def solve_knapsack(a, p, b):
    # number of items
    n = len(a)
    # initialize table
    table = np.zeros(shape=(n, b+1), dtype=int)

    # Initialize first row:
    for c in range(b + 1):
        if c >= a[0]:
            table[0, c] = p[0]

    # follow algorithm:
    for j in range(1, n):
        for c in range(0,b+1):
            
            if 0 <= c <= a[j]-1:
                # f(j, c) = f(j-1, c)
                table[j, c] = table[j-1, c]
            else:
                # f(j, c) = max{ f(j - 1, c); f(j-1, c-a_j) + pj}
                table[j,c] = max(table[j-1, c], table[j-1, c - a[j]] + p[j])
    
    return table, table[n-1, b]


def packed_items_list(table: np.ndarray, a, p,):
    num_items = table.shape[0]
    max_capacity = table.shape[1]


    # list of item indices; if 1, then item i is active <=> picked into the knapsack

    def backwards_algo(j, c, items_list = []):
        ...

        if j == 0:
            ...
            print("J = 1, stop here!")
            return
        else:
            ...
            
            if table[j,c] == table[j-1, c]:
                # item above has same value, so x_j = 0!
                items_list.append(0)
                return backwards_algo(j-1, c, items_list)
            else:
                # item is above and left
                ...

                val = table[j, c]
                val_above = table[j-1, c]
                val_above_left = table[j-1, c-a[j] + p[j]]

                if val == val_above:
                    ...
                    items_list.append(0)
                    return backwards_algo(j-1, c, items_list)
                elif val == val_above_left:
                    ...
                    items_list.append(1)
                    return backwards_algo(j-1, c-a[j], items_list)



                return backwards_algo(j-1, c, items_list)







    backwards_algo(j=2, c=5)


    for j in range(2,-1, -1):
        for c in range(num_items - 1, -1, -1):
            if j == 0:
                ...

            else:
                if table[j, c] == table[j-1,c]:
                    # item from above; x_j = 0
                    ...
                    print(f"item {j} is not packed.")
                








if __name__ == "__main__":


    # capacity of item j: a_j
    a = (2,4,3)
    # profit for packing item j: p_j
    p = (10,17,14)
    # Knapsack capacity: b=6
    b = 6
    table, optimal_solution = solve_knapsack(a, p, b)


    print("--- ", optimal_solution)

    items = packed_items_list(table, a, p)
    print("--- items: ", items)
            