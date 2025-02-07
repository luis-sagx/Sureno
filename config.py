from pymongo import MongoClient 

mongo_uri = "mongodb+srv://lsagnay:Ur9EcG84r3GJNegi@cluster0.ljtbc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client['Sureno']