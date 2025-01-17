import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter()

# File path to store flow data
DATA_FILE = "flowsAPI/flow_data.json"

class Question(BaseModel):
    question: str
    answer: str

# Define a Pydantic model for flow data
class FlowData(BaseModel):
    PAN: str
    phone: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None
    questions: Optional[List[Question]] = None


class UpdateFlowData(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None
    questions: Optional[List[Question]] = None

# Utility function to load data from the file
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file does not exist

# Utility function to save data to the file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

@router.post("/temp-flow-data")
def addFlowData(data: FlowData):
    """
    Function to add flow data. Ensures that PAN is unique.
    """
    # Load existing data
    flow_data_store = load_data()
    
    # Check if the PAN already exists
    for flow in flow_data_store:
        if flow["PAN"] == data.PAN:
            raise HTTPException(status_code=400, detail="Data with this PAN already exists.")
    
    # Add the new data
    flow_data_store.append(data.dict())
    save_data(flow_data_store)  # Save updated data to the file
    
    return {"message": "Flow data added successfully.", "data": data}

@router.get("/get-flow-data", response_model=List[FlowData])
def getFlowData():
    """
    Function to get all flow data.
    """
    flow_data_store = load_data()
    if not flow_data_store:
        raise HTTPException(status_code=404, detail="No flow data found.")
    
    return flow_data_store

@router.get("/temp-flow-data/{pan}", response_model=FlowData)
def getFlowDataByPAN(pan: str):
    """
    Function to get flow data for a specific PAN.
    """
    flow_data_store = load_data()
    
    # Search for the data by PAN
    for flow in flow_data_store:
        if flow["PAN"] == pan:
            return flow
    
    # If PAN not found, raise an exception
    raise HTTPException(status_code=404, detail=f"No data found for PAN: {pan}")


@router.patch("/temp-flow-data/{pan}")
def updateFlowData(pan: str, update_data: UpdateFlowData):
    """
    Function to update flow data for a specific PAN.
    Only updates the fields provided in the request body.
    """
    flow_data_store = load_data()
    print("PAN: ", pan)
    print("Data to be updated: ", update_data)
    # Search for the data by PAN
    for flow in flow_data_store:
        if flow["PAN"] == pan:
            # Update only the provided fields
            if update_data.name is not None:
                flow["name"] = update_data.name
            if update_data.phone is not None:
                flow["phone"] = update_data.phone
            if update_data.password is not None:
                flow["password"] = update_data.password
            if update_data.questions is not None:
                flow["questions"] = [q.dict() for q in update_data.questions]
            print("Updated flow data:", flow)  # Debugging line to see the updated flow

            save_data(flow_data_store)
            
            return {"message": "Flow data updated successfully.", "updated_data": flow}
    
    # If PAN not found, raise an exception
    raise HTTPException(status_code=404, detail=f"No data found for PAN: {pan}")