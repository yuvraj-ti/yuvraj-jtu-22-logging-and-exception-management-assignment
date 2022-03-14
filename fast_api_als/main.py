import time

from fastapi import FastAPI

from fast_api_als.routers import users, submit_lead, test_api

app = FastAPI()
app.include_router(users.router)
app.include_router(submit_lead.router)

# only present during test development
app.include_router(test_api.router)


@app.get("/")
def root():
    return {"message": "Hello, world!"}


@app.get("/ping")
def ping():
    start = time.process_time()
    time_taken = (time.process_time() - start) * 1000
    return {f"Pong with response time {time_taken} ms"}
