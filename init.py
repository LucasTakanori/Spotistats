from flask import app
from flask_pymongo import PyMongo
app.config["MONGO_URI"] = "mongodb+srv://lucastakanorisanchez:Pito@cluster00.tvlt0bo.mongodb.net/Spotistats"
pymongo = PyMongo(app)
