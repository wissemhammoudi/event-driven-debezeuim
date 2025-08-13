from fastapi import FastAPI

import routers.topic, routers.debezium,routers.consumer



app = FastAPI()

# Include Kafka routes
app.include_router(routers.topic.router)
app.include_router(routers.debezium.router)
app.include_router(routers.consumer.router)








@app.get("/")
def root():
    return {"message": "Event Driven Data ingestion service is running!"}
