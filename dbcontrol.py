from pymongo import MongoClient
client = MongoClient('mongodb://test:test@52.78.104.136', 27017)
db = client.dbchacha

# # 저장 - 예시
# doc = {'name':'bobby','age':21}
# db.users.insert_one(doc)

# # 한 개 찾기 - 예시
# user = db.tealist.find_one({'name':'둥굴레차'})

# # 여러개 찾기 - 예시 ( _id 값은 제외하고 출력)
# same_ages = list(db.users.find({'age':21},{'_id':False}))

# # 바꾸기 - 예시
# db.users.update_one({'name':'bobby'},{'$set':{'age':19}})
# #여러개를 바꿀 때는 update_many가 있지만 위험해서 잘 쓰지 않는다.

# db.tealist.update_one({'name':'커피'},{'$set':{'benefit':'피로회복 힐링힐링'}})
# db.tealist.update_one({'name':'결명자차'},{'$set':{'like':0}})
"""
scrap_id1 = db.tealist.find_one({'name': '세작'})
scrap_id2 = db.tealist.find_one({'name': '대작'})
id_list = []
id_list.append(scrap_id1['_id'])
id_list.append(scrap_id2['_id'])
print(id_list)
db.users.update_one({'id': "123"}, {'$set': {'scrap_id': id_list}}, True)
"""
"""
scrap_list = list(db.users.find({'id': '123'}))
a = scrap_list[0]['scrap_id']
for i in a:
   b = list(db.tealist.find({'_id':i}))
   print(b)
"""
check_scrap_id = db.users.find_one({'id': '123'})['scrap_id']
print(check_scrap_id)


# # 지우기 - 예시
# db.users.delete_one({'name':'bobby'})
# #여러개를 지울 때는 delete_many가 있지만 위험해서 잘 쓰지 않는다.