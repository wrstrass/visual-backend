from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import translate


app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class Chart(BaseModel):
    title: str | None = None
    xLabel: str | None = None
    yLabel: str | None = None
    type: str | None = None
    values: list[float]
    showValues: bool = True
    min: int | None = None
    max: int | None = None


class ChartChange(BaseModel):
    index: int
    values: list[float]
    charts: list[Chart]

    def detect_change(self):
        i = 0

        while (
            i < len(self.values) and self.values[i] == self.charts[self.index].values[i]
        ):
            i += 1

        return (
            (None, 0)
            if i == len(self.values)
            else (i, self.values[i] - self.charts[self.index].values[i])
        )

    def apply_change(self):
        self.charts[self.index].values = self.values

    def change_each_dealer_money_graph(self, arg: float | None = None):
        self.charts[2].max = self.S
        if arg == None:
            self.charts[2].values = [self.S / self.N] * self.N
        elif type(arg) == float:
            self.charts[2].values = [x + arg for x in self.charts[2].values]

    def change_dealer_max_amount_graph(self):
        self.charts[3].values = [int(self.S / 100)] * self.N

    def calc_result_product(self, add: bool = False):
        if add:
            self.charts += [None, None]

        dealers_product = translate.product_from_sum(
            S=self.charts[2].values,
            xE=[[i * self.S / 10 for i in range(11)]] * self.N,
            yE=[y.values for y in self.charts[4 : 4 + self.N]],
        )

        # algo debug prints
        print(self.charts[2].values)
        print([[i * self.S / 10 for i in range(11)]] * self.N)
        print([y.values for y in self.charts[4 : 4 + self.N]])
        print(dealers_product)

        self.charts[-2] = Chart(
            title="Dealer's Product",
            xLabel="Dealer",
            yLabel="Product",
            type="bar",
            values=dealers_product,
            min=0,
        )

        self.charts[-1] = Chart(
            title="Dealer's Product Percentage (FIXED)",
            xLabel="Dealer",
            yLabel="Product %",
            type="bar",
            values=translate.get_percentage(dealers_product),
            min=0,
        )

    def reset_dealer_sell_step(self, index: int | None = None):
        if index == None:
            left = 4
            right = 4 + self.N
        else:
            left = 4 + index
            right = 5 + index

        for i in range(left, right):
            self.charts[i].xLabel = "Money (step = " + str(self.S / 10) + "$)"
            self.charts[i].max = self.charts[3].values[i - 4]
            self.charts[i].values = [
                j * (self.charts[i].max / 10) for j in range(0, 11)
            ]

    def add_dealer_sell_graphs(self):
        self.charts += [
            Chart(
                title="Dealer " + str(i + 1) + " sell graph",
                xLabel="Money (step = " + str(self.S / 10) + "$)",
                yLabel="Product Amount",
                values=list(range(0, 110, 10)),
                min=0,
                max=self.charts[3].values[i],
            )
            for i in range(self.N)
        ]

    @property
    def S(self):
        return self.charts[0].values[0]

    @property
    def N(self):
        return int(self.charts[1].values[0])


@app.get("/api")
async def initial():
    return [
        Chart(
            title="Money",
            type="bar",
            values=[
                10000,
            ],
            min=0,
            max=50000,
        ),
        Chart(
            title="Dealers Amount",
            type="bar",
            values=[
                3,
            ],
            min=0,
            max=10,
        ),
        Chart(
            title="Each Dealer Money",
            xLabel="Dealer",
            yLabel="Money",
            type="bar",
            values=[10000 / 3] * 3,
            min=0,
            max=10000,
        ),
        Chart(
            title="Dealer Max Amount",
            xLabel="Dealer",
            yLabel="Max Amount",
            type="bar",
            values=[int(10000 / 100)] * 3,
            min=0,
        ),
    ]


@app.post("/api")
async def change(chart_change: Request):
    chart_change = await chart_change.json()
    try:
        chart_change = ChartChange(**chart_change)
    except Exception as exc:
        return {"exc": str(exc)}
    # print(chart_change)

    column, delta = chart_change.detect_change()
    if column == None and chart_change.index == 1:
        column = 0
    print(chart_change.index, column, delta)

    redraw = {
        "summ": False,
        "dealers_money": False,
        "dealer_sell_graph": False,
        "result": {},
    }

    chart_change.apply_change()

    # money change
    if chart_change.index == 0:
        chart_change.change_each_dealer_money_graph(delta / chart_change.N)
        chart_change.reset_dealer_sell_step()
        chart_change.calc_result_product()

    # N changed
    if chart_change.index == 1 and column == 0:
        chart_change.charts = chart_change.charts[:4]
        print(chart_change.S, chart_change.N)

        chart_change.change_each_dealer_money_graph()
        chart_change.change_dealer_max_amount_graph()
        chart_change.add_dealer_sell_graphs()

        chart_change.calc_result_product(add=True)

    # dealer max money change
    if chart_change.index == 2:
        left_amount = column + 1
        right_amount = chart_change.N - left_amount
        left_sum = sum(chart_change.charts[2].values[0:left_amount])
        if left_sum > chart_change.S:
            chart_change.change_each_dealer_money_graph(
                (chart_change.S - left_sum) / (left_amount)
            )
            left_sum = chart_change.S
        chart_change.charts[2].values = (
            chart_change.charts[2].values[:left_amount]
            + [(chart_change.S - left_sum) / (right_amount)] * right_amount
        )

        chart_change.calc_result_product()

    # dealer max amount change
    if chart_change.index == 3:
        chart_change.reset_dealer_sell_step(column)
        chart_change.calc_result_product()

    # dealer sell graph change
    if 4 <= chart_change.index < 4 + chart_change.N:
        chart_change.calc_result_product()

    if chart_change.index == 4 + chart_change.N:
        chart_change.charts[2].values = translate.sum_from_product(
            P=chart_change.values,
            xE=[[i * chart_change.S / 10 for i in range(11)]] * chart_change.N,
            yE=[y.values for y in chart_change.charts[4 : 4 + chart_change.N]],
        )

    # if redraw["result"] != False:
    #     chart_change.calc_result(**redraw["result"])

    # print(chart_change.charts)
    return chart_change.charts
