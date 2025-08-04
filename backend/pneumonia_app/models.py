from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client['pneumoniaDB']
users = db['users']    #users folder
results_collection = db['results']    #results folder