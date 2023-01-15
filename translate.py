from scipy.interpolate import interp1d


def get_percentage(lst: list[int]):
    return [el / sum(lst) * 100 for el in lst]


def product_from_sum(S: list[int], xE: list[list[int]], yE: list[list[int]]):
    """
    PARAMETERS:

    S - sum, given to each provider;

    xE and yE - 2-dim lists: every row is a list of E function x-values and y-values for every provider;

    RETURN VALUE:

    Product count list.
    """

    E_funcs = [interp1d(xE[i], yE[i], kind="cubic") for i in range(len(xE))]
    return [int(E_funcs[i](S[i])) for i in range(len(S))]


def sum_from_product(P: list[int], xE: list[list[int]], yE: list[list[int]]):
    """
    PARAMETERS:

    P - product, required from each provider;

    xE and yE - 2-dim lists: every row is a list of E function x-values and y-values for every provider;

    RETURN VALUE:

    Sums amount list.
    """

    E_funcs = [interp1d(yE[i], xE[i], kind="cubic") for i in range(len(xE))]
    return [int(E_funcs[i](P[i])) for i in range(len(P))]
