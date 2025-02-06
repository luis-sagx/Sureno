from pymongo import MongoClient 
import os

class Config:
    MONGO_URI = 'mongodb+srv://lsagnay:Ur9EcG84r3GJNegi@cluster0.ljtbc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

client = MongoClient(Config.MONGO_URI)

db = client.Sureno  
