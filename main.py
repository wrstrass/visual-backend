from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class Chart(BaseModel):
    title: str | None = None
    xLabel: str | None = None
    yLabel: str | None = None
    type: str | None = None
    values: list[int]
    showValues: bool = True
    min: int | None = None
    max: int | None = None


class ChartChange(BaseModel):
    index: int
    values: list[int]
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

    @property
    def S(self):
        return self.charts[0].values[1]

    @property
    def N(self):
        return self.charts[1].values[1]


@app.get("/api")
async def initial():
    return [
        Chart(
            title="Money",
            type="bar",
            values=[10000, 10000],
            min=0,
        ),
        Chart(
            title="Dealers Amount",
            type="bar",
            values=[3, 3],
            min=0,
            max=10,
        ),
    ]


@app.post("/api")
async def change(chart_change: Request):
    chart_change = await chart_change.json()
    try:
        chart_change = ChartChange(**chart_change)
    except Exception as exc:
        return {"exc": str(exc)}
    print(chart_change)

    column, delta = chart_change.detect_change()
    if column == None and chart_change.index == 1:
        column = 1
    print(column, delta)

    # reference columns don't change
    if not ((chart_change.index == 0 or chart_change.index == 1) and column == 0):
        chart_change.apply_change()

    # N changed
    if chart_change.index == 1 and column == 1:
        chart_change.charts = chart_change.charts[:2]
        print(chart_change.S, chart_change.N)

        chart_change.charts.append(
            Chart(
                title="Each Dealer Money",
                xLabel="Dealer",
                yLabel="Money",
                type="bar",
                values=[chart_change.S / chart_change.N] * chart_change.N,
                min=0,
                max=chart_change.S,
            )
        )
        chart_change.charts.append(
            Chart(
                title="Dealer Max Amount",
                xLabel="Dealer",
                yLabel="Max Amount",
                type="bar",
                values=[int(chart_change.S / 100)] * chart_change.N,
                min=0,
            )
        )

        chart_change.charts += [
            Chart(
                title="Dealer " + str(i + 1) + " sell graph",
                xLabel="Money (step = " + str(chart_change.S / 10) + "$)",
                yLabel="Product Amount",
                values=[10 * j for j in range(11)],
                min=0,
                max=chart_change.charts[3].values[i],
            )
            for i in range(chart_change.N)
        ]

    print(chart_change.charts)
    return chart_change.charts
