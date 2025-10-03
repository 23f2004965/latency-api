from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
from pathlib import Path

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Load telemetry data once
data_file = Path("q-vercel-latency.json")
with open(data_file) as f:
    telemetry = pd.DataFrame(json.load(f))

@app.post("/latency")
async def check_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    results = {}

    for region in regions:
        df = telemetry[telemetry["region"] == region]
        if df.empty:
            continue
        avg_latency = df["latency_ms"].mean()
        p95_latency = np.percentile(df["latency_ms"], 95)
        avg_uptime = df["uptime_pct"].mean()
        breaches = int((df["latency_ms"] > threshold).sum())

        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 3),
            "breaches": breaches,
        }

    return results
