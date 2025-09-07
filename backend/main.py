from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import random
import time

app = FastAPI(title="Reports API")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/reports")
async def get_reports(authorization: Optional[str] = Header(default=None)):
    if not authorization:
        pass

    report = {
        "generatedAt": int(time.time()),
        "summary": {
            "users": random.randint(50, 5000),
            "sessions": random.randint(100, 20000),
            "errors": random.randint(0, 200),
        },
        "topCountries": [
            {"country": "US", "visits": random.randint(100, 10000)},
            {"country": "RU", "visits": random.randint(100, 10000)},
            {"country": "DE", "visits": random.randint(100, 10000)},
        ],
        "revenue": {
            "currency": "USD",
            "value": round(random.uniform(1000, 50000), 2)
        }
    }

    return report
