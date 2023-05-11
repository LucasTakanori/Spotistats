import datetime   # This will be needed later
import os
import pprint
import bson
import pymongo
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from pprint import pprint

# Load config from a .env file:
load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']

# Connect to your MongoDB cluster:
client = MongoClient(MONGODB_URI)

db = client['Spotistats']
# List all the databases in the cluster:
#ç

users = db['Users']
# Find the user with the specified _id:
user = users.find_one({'_id': ObjectId('645adada267aa18e350d8b1c')})

# Pretty-print the user document:
pprint(user)

