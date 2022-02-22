import random
from urllib import response
from flask import Flask, render_template, request, jsonify, make_response
from flask_jwt_extended import *
from flask_bcrypt import *
import hashlib
from hashlib import *
import datetime
import chachaconfig
import pandas as pd
import random
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 현상 해결코드

# configure Flask App with Flask RESTFUL API
# Flask RESTFUL API로 Flask App 구성
# api = Api(app)

app.config['JWT_SECRET_KEY'] = chachaconfig.jwt_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=5)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=10)
app.config['JWT_ACCESS_COOKIE_NAME'] = 'chachaAccessToken'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'chachaRefreshToken'
app.config['JWT_TOKEN_LOCATION'] = ["cookies"]
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SESSION_COOKIE_SECURE'] = True

# configure Flask App with JWT support
# JWT 지원으로 Flask App 구성
jwt = JWTManager(app)

# DB 관련
from pymongo import MongoClient, ReturnDocument

# 서버 db 사용시 로컬 db 주석 처리, 로컬 db 사용시 서버 db 주석 처리
# **********************************************************


# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://test:test@52.78.104.136', 27017)


db = client.dbchacha


# **********************************************************


# 차 정보 입력하기(POST) API _ 재영

@app.route('/save', methods=['POST'])
def save_tea():
    print(request.is_json)
    tea_receive = request.get_json()
    name_receive = tea_receive['name_give']                     # 차 이름입니다
    # eng_name_receive = tea_receive['eng_name_give']             # (영문)차 이름입니다 - 사용 않아서 주석처리
    type_receive = tea_receive['type_give']                     # 대분류1 종류
    eng_type_receive = tea_receive['eng_type_give']             # 대분류1 (영문)종류 - 종류 선택시 자동 입력
    benefit_receive = tea_receive['benefit_give']               # 대분류2 효능
    caffeineOX_receive = tea_receive['caffeineOX_give']         # 대분류3 카페인 "함유여부" Boolean 없으면 False 있으면 True
    caffeine_receive = tea_receive['caffeine_give']             # 상세1 카페인 "함량"
    benefitdetail_receive = tea_receive['benefitdetail_give']   # 상세2 상세효능
    desc_receive = tea_receive['desc_give']                     # 상세2 상세설명
    caution_receive = tea_receive['caution_give']               # 상세3 주의사항
    img_receive = tea_receive['img_give']                       # 상세4 이미지 주소

    doc = {
        'name': name_receive,
         # 'eng_name': eng_name_receive,
        'type': type_receive,
        'eng_type': eng_type_receive,
        'benefit': benefit_receive,
        'caffeineOX': caffeineOX_receive,
        'caffeine': caffeine_receive,
        'benefitdetail': benefitdetail_receive,
        'desc': desc_receive,
        'caution': caution_receive,
        'img': img_receive,
    }

    db.tealist.insert_one(doc)

    return jsonify({'msg': '차 등록이 완료되었습니다!'})


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/index')
def index_page():
    return render_template('index.html')

@app.route('/info')
def info_page():
    return render_template('info.html')

@app.route('/info_edit')
def info_edit_page():
    return render_template('info_edit.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/manager')
def manager_page():
    return render_template('manager.html')

@app.route('/tea_list')
def tea_list_page():
    return render_template('tea_list.html')




@app.route('/save_tea')
def saveTea():
    return render_template('save_tea.html')






# ***************************************************************************************************

# 차 추천기능 (카테고리 선택에 의함) _ 재영
# 대체 어제는 왜 for문을 돌렸는데 됐을까? 명백히 논리적으로 오류인데 어째서 결과가 나왔던 걸까?
# 어쨌든 더 찾아보고 더 파서 해냈다 ㄱㄱㅌㄱ

@app.route('/recommend/find', methods=['POST'])
def read_mongo():
    # df_all : Pandas(패키지)로 데이터프레임 형태를 만들어, DB 전체를 불러온다.
    data_list = list(db.tealist.find({}, {'_id': False}))

    random.shuffle(data_list)
    df_all = pd.DataFrame(data_list)

    selector_receive = request.get_json()
    type_receive = selector_receive['type_give']
    benefit_receive = selector_receive['benefit_give']
    caffeineOX_receive = selector_receive['caffeineOX_give']

    # df_type : 전체 데이터프레임(df_all)에서 type이 '같은' 항목들만 받아서 새로 데이터프레임을 만든다.
    df_type = df_all.loc[df_all['type'].isin(type_receive)]
    df_type.head()

    # df_benefit : type 으로 걸러낸 데이터프레임(df_type) 중에서, benefit이 맞는 정보들만 받아서 새로운 데이터프레임을 만든다.
    # benequery : 데이터프레임에서 어떤 조건으로 검색할지 query문을 만들어주기 위한 문자 함수이다.
    # 입력받는 효능의 갯수가 불확실한 상황에서, DB상의 "효능"란에 입력받은 값이 '포함' 되는지를 비교할 기능을 찾지 못했다.
    # 우리가 입력받은 효능 값의 개수만큼 for 문을 돌려서 아래와 같이 query 문을 만들었다.
    # 예시: (@df_type['benefit'].str.contains ('다이어트')) or (@df_type['benefit'].str.contains('피부미용'))
    benequery = f"(@df_type['benefit'].str.contains ('"
    for i in range(len(benefit_receive)):
        if i < len(benefit_receive) - 1:
            benequery += benefit_receive[i] + f"')) or (@df_type['benefit'].str.contains('"
        else:
            benequery += benefit_receive[i] + f"'))"
    print(benequery)
    df_benefit = df_type.query(benequery)
    df_benefit.head()

    # df_caffeine : benefit 으로 걸러낸 데이터프레임(df_benefit) 중에서, caffeineOX가 '같은' 항목들만 받아서 새로운 데이터프레임을 만든다.
    df_caffeine = df_benefit.loc[df_benefit['caffeineOX'].isin(caffeineOX_receive)]
    df_caffeine.head()

    # 다 걸러진 결과값을 JSON 형식으로 바꿔준다. (JSON 형식을 갖는 string으로 저장됨! 클라이언트에서 parsing)
    find_list = df_caffeine.to_json(orient='records', force_ascii=False)

    return jsonify({'find_teas': find_list})

@app.route('/recommend')  # 검색창 부분 건드리지 않으려고 우선 따로 만들어봄, 병합시 삭제 또는 수정
def recommend_page():
    return render_template('recommend_tea.html')

# ***************************************************************************************************




# ***************************************************************************************************

# 티 정보 GET 하기 -- 영은
@app.route('/tea/list', methods=['GET'])
def getTea():
    tea_List = list(db.tealist.find({}, {'_id': False}))
    random.shuffle(tea_List)  # 랜덤 정렬 good good
    return jsonify({'all_teas':tea_List})

# 검색 기능 -- 영은
@app.route('/tea/search', methods=['POST'])
def searchTea():
    df_all = pd.DataFrame(list(db.tealist.find({}, {'_id': False})))

    keyword_receive = request.get_json()['teaKeyword']

    df_search = df_all[df_all['name'].str.contains(keyword_receive)]

    find_list = df_search.to_json(orient='records', force_ascii=False)

    return jsonify({'search_teas': find_list})


@app.route('/tea')
def teaList():
    return render_template('get_tea.html')


# ***************************************************************************************************

# like+scrap -- 승신

# ***************************************************************************************************

@app.route('/tea/like_all', methods=['POST'])
@jwt_required()
def like_all():
    current_user = get_jwt_identity().upper()
    name_receive = request.form['name_give']
    target_tea = db.tealist.find_one({'name': name_receive})
    current_like = target_tea['like']
    check_scrap_id = db.users.find_one({'user_id': current_user})['scrap_id']


    if check_scrap_id is not None:
        return jsonify({'alreadyScrap': '이미 찜 하셨습니다.'})
    else:
        new_like = current_like + 1
        db.tealist.update_one({'name': name_receive}, {'$set': {'like': new_like}})
        scrap_id = db.tealist.find_one({'name': name_receive})
        id_list = []
        id_list.append(scrap_id)
        db.users.update_one({'id': current_user}, {'$set': {'scrap_id': id_list}}, True)
        return jsonify({'successScrap': '좋아요, 찜 완료.'})

# ***************************************************************************************************

@app.route('/tea/scrapList', methods=['GET'])
@jwt_required()
def showScrapTea():
    current_user = get_jwt_identity().upper()
    check_id_list = db.users.find_one({'user_id': current_user})
    if check_id_list is not None:
        scrap_list = list(db.users.find({'id': '123'}))
        a = scrap_list[0]['scrap_id']
        for i in a:
            b = list(db.tealist.find({'_id': i}))
        return jsonify({'scrapTeas': b})
    else:
        return jsonify({'msg': '비어있습니다'})


@app.route('/tea/deleteScrap', methods=['POST'])
@jwt_required()
def delete_scrap():
    name_receive = request.form['name_give']
    db.scraps.delete_one({'name': name_receive})
    return jsonify({'msg': '삭제 완료'})


@app.route('/tea/scrapPage')
def scrapPage():
    return render_template('tea_scrap.html')


# ***************************************************************************************************

# ***************************************************************************************************
# mu-jun's function code

#  signup
@app.route('/sign/checkID', methods=['POST'])
def checkID():
    print('checkID start')

    id_receive = request.get_json().upper()
    result = db.users.find_one({'id': id_receive})

    if result is not None:
        return jsonify({'fail': '사용할 수 없는 ID입니다.'})
    else:
        return jsonify({'success': '사용 가능한 ID입니다.'})


@app.route('/sign/checkNickname', methods=['POST'])
def checkNickname():
    print('checkNickname start')

    nickname_receive = request.get_json().upper()

    result = db.users.find_one({'id': nickname_receive})

    if result is not None:
        return jsonify({'fail': '사용할 수 없는 별명입니다.'})
    else:
        return jsonify({'success': '사용 가능한 별명입니다.'})


# 반복 솔팅?
def hash_pass(password, id):
    personal_key = id[:8].encode('utf-8')
    password = password + chachaconfig.salt_key

    for i in range(chachaconfig.iteration_num):
        password = password.encode('utf-8')
        password = blake2s(password, person=personal_key).hexdigest()

    return password


@app.route('/sign/signup', methods=['POST'])
def signup():
    print('signup start')

    receive = request.get_json();
    print(receive)

    id_receive = receive['id_give'].upper()
    pass_receive = receive['pass_give']
    nickname_receive = receive['nickname_give'].upper()

    hashed_password = hash_pass(pass_receive, id_receive)

    doc = {
        'id': id_receive,
        'password': hashed_password,
        'nickname': nickname_receive
    }

    print(doc)
    db.users.insert_one(doc)

    return jsonify({'success': '가입완료!'})


# sign in
@app.route('/sign/signin', methods=['POST'])
def api_signin():
    print('signin start')
    response = make_response(render_template('/login.html'))
    receive = request.get_json();

    id_receive = receive['id_give'].upper()
    pass_receive = receive['pass_give']

    print(id_receive)

    hashed_password = hash_pass(pass_receive, id_receive)

    user = db.users.find_one({'id': id_receive})
    print(user)

    if (user):
        if (hashed_password == user['password']):
            response = jsonify({'success': '환영합니다.' + user['nickname'] + '님'})

            access_token = create_access_token(identity=user['id'])
            #response.set_cookie('chachaAccessToken', value=access_token, samesite=None, httponly=True)
            set_access_cookies(response,access_token)
            refresh_token = create_refresh_token(identity=user['id'])
            #response.set_cookie('chachaRefreshToken', value=refresh_token, samesite=None, httponly=True)
            set_refresh_cookies(response,refresh_token)

            return response
    else:
        return jsonify({'fail': 'ID와 비밀번호를 확인해주세요.'})


# cookie 토큰관리

@app.route('/unset_token', methods=['GET'])
def set_access_token():
    print('unset_token start')
    response = make_response(render_template('/login.html'))

    response.delete_cookie('chachaAccessToken')
    response.delete_cookie('chachaRefreshToken')

    return response


@app.route('/get_access_token', methods=['GET'])
def api_get_access_token():
    print('get_access_token start')

    result = request.cookies.get('chachaAccessToken')

    if result is not None:
        return jsonify(result)
    else:
        return jsonify(None)


@app.route('/get_refresh_token', methods=['GET'])
def api_get_refresh_token():
    print('get_refresh_token start')

    result = request.cookies.get('chachaRefreshToken')
    print(result)
    if result is not None:
        return jsonify(result)
    else:
        return jsonify(None)


@app.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    print('refresh start')

    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token, current_user=current_user)


# sign information 유저정보변경
@app.route('/sign/change_pass', methods=['POST'])
@jwt_required()
def api_change_pass():
    print('change_pass start')
    current_user = get_jwt_identity().upper()
    print(current_user)

    print(request.get_data())
    receive = request.get_json()
    print(receive)

    pass_receive = receive['pass_give']
    new_password = receive['new_pass_give']

    hashed_password = hash_pass(pass_receive, current_user)
    new_password = hash_pass(new_password, current_user)

    user = db.users.find_one({'id': current_user})

    print(user)
    if (user):
        if (hashed_password == user['password']):
            db.users.update_one({'id': current_user}, {'$set': {'password': new_password}})
            return jsonify({'success': '비밀번호가 변경되었습니다.'})
        else:
            return jsonify({'fail': '기존 비밀번호가 틀렸습니다.'})
    else:
        return jsonify({'fail': '로그인 먼저 해주세요.'})


@app.route('/sign/delete_user', methods=['POST'])
@jwt_required()
def api_delete_user():
    print('delete_user start')

    current_user = get_jwt_identity().upper()
    receive = request.get_json()
    password = receive['pass_give']

    hashed_password = hash_pass(password, current_user)

    user = db.users.find_one({'id': current_user})

    if (user):
        if (hashed_password == user['password']):
            db.users.delete_one({'id': current_user})
            print('success')
            return jsonify({'success': '탈퇴하셨습니다.'})
        else:
            print('fail2')
            return jsonify({'fail': '기존 비밀번호가 틀렸습니다.'})
    else:
        print('fail1')
        return jsonify({'fail': '로그인 먼저 해주세요.'})


@app.route('/sign_test')
def sign_page():
    return render_template('login.html')


# ***************************************************************************************************
if __name__ == '__main__':
    app.run('0.0.0.0',port=5001,debug=True)

# 안 쓰는데 혹시나 해서 남겨둔 예전 like & scrap *********************************************************

"""
# ***************************************************************************************************
# like --승신
# ***************************************************************************************************
@app.route('/tea/like', methods=['POST'])
@jwt_required()
def likeTea():
    name_receive = request.form['name_give']
    target_tea = db.tealist.find_one({'name': name_receive})
    current_like = target_tea['like']
    new_like = current_like + 1
    db.tealist.update_one({'name': name_receive}, {'$set': {'like': new_like}})
    return jsonify({'msg': 'like +1'})
# ***************************************************************************************************
# scrap --승신
# 찜 오류 해결 (해결하고나서 보니 매우 간단하게 해결 가능했다는 점이 빡침 포인트)
# ***************************************************************************************************
@app.route('/tea/scrap', methods=['POST'])
@jwt_required()
def scrapTea():
    current_user = get_jwt_identity().upper()
    name_receive = request.form['name_give']
    check_scrap_name = db.scraps.find_one({'name': name_receive})
    check_scrap_id = db.scraps.find_one({'user_id': current_user})
    if check_scrap_id == current_user:
        return jsonify({'alreadyScrap': '이미 찜 하셨습니다.'})
    else:
        db.tealist.update_one({'name': name_receive}, {'$set': {'user_id': current_user}}, True)
        scrap_list = db.tealist.find_one({'name': name_receive}, {'_id': False})
        db.scraps.insert_one(scrap_list)
        return jsonify({'successScrap': '찜 완료 되었습니다.'})
"""