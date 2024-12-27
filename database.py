from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['twitter_trends']
        self.collection = self.db['trends']

    def save_trends(self, trends_data):
        return self.collection.insert_one(trends_data)

    def get_latest_trends(self):
        return self.collection.find_one(sort=[('timestamp', -1)]) 