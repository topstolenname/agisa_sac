from fastapi import FastAPI

app = FastAPI(title="AGI-SAC PCP")


@app.get("/pcp/agent/telemetry")
async def agent_telemetry():
    return {"status": "ok"}


@app.post("/pcp/resonance-scan")
async def resonance_scan():
    return {"detected": False}
