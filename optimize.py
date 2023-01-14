from ortools.linear_solver import pywraplp


def optimize_sum(N: int, s: int, xE: list[list[int]], yE: list[list[int]],
                 fixed_money: dict[int, int], fixed_products: dict[int, int], mode='one'):
    """
    PARAMETERS:

    N - provider count;

    s - given sum;

    xE and yE - 2-dim lists: every row is a list of E function x-values and y-values for every provider;

    fixed_money - dict that: key is index of fixed provider, value is money we give to a provider;
    pass empty dict if no points;

    fixed_products - dict that: key is index of fixed provider, value is product amount we want to get from provider;
    pass empty dict if no points;

    mode - available modes:

    "one" - one E function for every provider;

    "many" - every line of E list is a new function;

    "one" is default;

    E list must have length of 1 in "one" mode;
    E list must have length of N in "many" mode.

    RETURN VALUE:

    Money list and products list.
    """

    solver = pywraplp.Solver.CreateSolver("SCIP")

    x_axis, y_axis = _create_axis(N, xE, yE, mode)
    cut_x_axis, cut_y_axis = [], []

    for i in range(N):
        if i in fixed_money:
            s -= fixed_money[i]
            continue
        if i in fixed_products:
            fixed_money[i] = _product_to_money(fixed_products[i], x_axis[i], y_axis[i])
            s -= fixed_money[i]
            continue
        cut_x_axis.append(x_axis[i])
        cut_y_axis.append(y_axis[i])

    x = [solver.IntVar(0, s, f"x{i}") for i in range(N - len(fixed_money))]

    solver.Add(sum([x[i] for i in range(N - len(fixed_money))]) == s)

    solver.Maximize(sum([_linear_interpolate(x[i], cut_x_axis[i], cut_y_axis[i]) for i in range(N - len(fixed_money))]))

    solver.Solve()

    return _get_res(N, x_axis, y_axis, fixed_money, x)


def _create_axis(N: int, xE: list[list[int]], yE: list[list[int]], mode: str):
    if mode == "one":
        if len(xE) != 1 or len(yE) != 1:
            raise ValueError("E length must be 1 in 'one' mode!")
        x_axis = [xE[0].copy() for _ in range(N)]
        y_axis = [yE[0].copy() for _ in range(N)]
    elif mode == "many":
        if len(xE) != N or len(yE) != N:
            raise ValueError("E length must be N in 'many' mode!")
        x_axis = xE.copy()
        y_axis = yE.copy()
    else:
        raise NotImplemented
    return x_axis, y_axis


def _product_to_money(product_value: int, x_axis: list[int], y_axis: list[int]):
    for i in range(len(y_axis) - 1):
        if y_axis[i] <= product_value <= y_axis[i + 1]:
            return (x_axis[i + 1] - x_axis[i]) * (product_value - y_axis[i]) // (y_axis[i + 1] - y_axis[i]) + x_axis[i]
    raise ValueError("product_value not in right interval")


def _linear_interpolate(x_val, x_axis: list[int], y_axis: list[int]):
    for i in range(len(x_axis) - 1):
        if x_axis[i] <= x_val <= x_axis[i + 1]:
            return (y_axis[i + 1] - y_axis[i]) * (x_val - x_axis[i]) / (x_axis[i + 1] - x_axis[i]) + y_axis[i]
    raise ValueError("x_val not in right interval")


def _get_res(N: int, x_axis: list[list[int]], y_axis: list[list[int]], fixed_money: dict[int, int], x: list):
    moneys = []
    fixed_count = 0
    for i in range(N):
        if i in fixed_money:
            moneys.append(fixed_money[i])
            fixed_count += 1
            continue
        moneys.append(int(x[i - fixed_count].solution_value()))
    return moneys, [int(_linear_interpolate(moneys[i], x_axis[i], y_axis[i])) for i in range(N)]


# if __name__ == "__main__":
#     print(optimize_sum(5, 10000, [[0, 1000, 2000, 3000, 4000, 5000, 10000]], [[0, 10, 20, 30, 40, 50, 100]], {}, {2: 50}))
