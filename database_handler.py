from pymongo import MongoClient
import os
import uuid
from datetime import datetime

# MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "brain_tumor_db"
COLLECTION_NAME = "scan_records"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def generate_patient_id(name, phone):
    base = (name + phone).lower().replace(" ", "")
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, base))

def generate_scan_id():
    return str(uuid.uuid4())

def save_new_patient_scan(
    patient_name,
    patient_age,
    patient_gender,
    phone,
    email,
    doctor_name,
    original_file_path,
    segmented_image_path
):
    patient_id = generate_patient_id(patient_name, phone)
    scan_id = generate_scan_id()
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = {
        "patient_id": patient_id,
        "scan_id": scan_id,
        "patient_name": patient_name,
        "patient_age": patient_age,
        "patient_gender": patient_gender,
        "phone": phone,
        "email": email,
        "doctor_name": doctor_name,
        "scan_date": scan_date,
        "original_image_paths": original_file_path,
        "segmented_image_path": segmented_image_path
    }

    result = collection.insert_one(record)
    return {
        "inserted_id": str(result.inserted_id),
        "patient_id": patient_id,
        "scan_id": scan_id,
        "scan_date": scan_date
    }

def save_existing_patient_scan(
    patient_id,
    original_file_path,
    segmented_image_path
):
    scan_id = generate_scan_id()
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = {
        "patient_id": patient_id,
        "scan_id": scan_id,
        "scan_date": scan_date,
        "original_image_paths": original_file_path,
        "segmented_image_path": segmented_image_path
    }

    result = collection.insert_one(record)
    return {
        "inserted_id": str(result.inserted_id),
        "patient_id": patient_id,
        "scan_id": scan_id,
        "scan_date": scan_date
    }

def get_scan_history(patient_id=None, scan_date=None):
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    if scan_date:
        query["scan_date"] = {"$regex": scan_date}

    return list(collection.find(query, {"_id": 0}))

def delete_scan_record(scan_id):
    result = collection.delete_one({"scan_id": scan_id})
    return result.deleted_count > 0
