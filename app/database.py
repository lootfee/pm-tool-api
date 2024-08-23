from pymongo import MongoClient

# client = MongoClient('localhost', 27017) # username=app.config['DB_USERNAME'], password=app.config['DB_PASSWORD']
# db = client["pm-tool"]


# class UsersDb:
#     def __init__(self):
#         self.col = db["users"]
        
#     @classmethod
#     def save(self, data):
#         self.col.insert_one(data)
        
#     @classmethod
#     def load_one(self, query):
#         return self.col.find_one(query)
    
#     @classmethod
#     def load_many(self, query):
#         return list(self.col.find(query))


# class ProjectsDb:
#     def __init__(self):
#         self.col = db["projects"]
        
#     @classmethod
#     def save(self, data):
#         self.col.insert_one(data)
        
#     def load_one(self, query):
#         return self.col.find_one(query)
    
#     def load_many(self, query):
#         return list(self.col.find(query))
    
    
# class TokensDb:
#     def __init__(self):
#         self.col = db["tokens"]
        
#     @classmethod
#     def save(self, data):
#         self.col.insert_one(data)
        
#     def load_one(self, query):
#         return self.col.find_one(query)
    
#     def load_many(self, query):
#         return list(self.col.find(query))
    
#     def delete_one(self, query):
#         self.col.delete(query)
    
#     def delete_many(self, query):
#         self.col.delete_many(query)
    

class Database:
    print('database')
    def __init__(self, collection_name):
        client = MongoClient('localhost', 27017)  # Add username and password if needed
        db = client["pm-tool"]
        self.col = db[collection_name]
        
    def save(self, data):
        self.col.insert_one(data)
        
    def load_one(self, query):
        return self.col.find_one(query)
    
    def load_all(self):
        return list(self.col.find())
    
    def delete_one(self, query):
        self.col.delete_one(query)
    
    def delete_many(self, query):
        self.col.delete_many(query)