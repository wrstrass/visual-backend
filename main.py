from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class Chart(BaseModel):
    values: list[int]
    type: str | None = None
    min: int | None = None
    max: int | None = None


class ChartChange(BaseModel):
    index: int
    values: list[int]
    charts: list[Chart]


@app.get("/api")
async def initial():
    return [Chart(values=[10, 20, 30, 40, 50], min=0, max=70, type="bar")] * 2


@app.post("/api")
async def change(chart_change: Request):
    chart_change = await chart_change.json()
    try:
        chart_change = ChartChange(**chart_change)
    except Exception as exc:
        return {"exc": str(exc)}

    chart_change.charts[chart_change.index].values = chart_change.values

    return chart_change.charts
