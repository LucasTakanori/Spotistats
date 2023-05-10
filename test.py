import pymongo

myclient = pymongo.MongoClient("mongodb+srv://lucastakanorisanchez:Pito@cluster00.tvlt0bo.mongodb.net/")
mydb = myclient["Spotistats"]
users=mydb["Users"]
pito=users.find({'email' : 'lucastakanori13@gmail.com'})
for x in pito:
	print(x)
#print("You are successfully connected to MongoDB!")