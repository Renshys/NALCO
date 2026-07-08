from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

from database import predictions_collection

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

model = joblib.load("../model/model.pkl")


class MachineData(BaseModel):
    Type: int
    air_temperature: float
    process_temperature: float
    rotational_speed: int
    torque: float
    tool_wear: int


@app.get("/")
def home():
    return {
        "message": "NALCO Equipment Failure Prediction API is Running"
    }


@app.post("/predict")
def predict(data: MachineData):

    input_data = pd.DataFrame({
        "Type": [data.Type],
        "Air temperature [K]": [data.air_temperature],
        "Process temperature [K]": [data.process_temperature],
        "Rotational speed [rpm]": [data.rotational_speed],
        "Torque [Nm]": [data.torque],
        "Tool wear [min]": [data.tool_wear]
    })

    prediction = model.predict(input_data)

    if prediction[0] == 0:
        result = "Healthy"
    else:
        result = "Failure"

    prediction_document = {
        "Type": data.Type,
        "Air Temperature": data.air_temperature,
        "Process Temperature": data.process_temperature,
        "Rotational Speed": data.rotational_speed,
        "Torque": data.torque,
        "Tool Wear": data.tool_wear,
        "Prediction": result,
        "Created At": datetime.utcnow()
    }

    predictions_collection.insert_one(prediction_document)

    return {
        "prediction": result
    }
@app.get("/history")
def get_history():
    history = []

    for document in predictions_collection.find():
        document["_id"] = str(document["_id"])
        history.append(document)

    return history

