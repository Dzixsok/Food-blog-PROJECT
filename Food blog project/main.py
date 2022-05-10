# 1-1 导入flask需要的库
import pymongo
from bson import ObjectId
from flask import Flask, render_template, request, session, redirect

# 1-2 使用Flask创建一个flask对象
app = Flask(__name__)

# 1-3 连接MongoDB数据库(数据库名称:menu,集合名称:content)
client = pymongo.MongoClient(host='127.0.0.1', port=27017)
menu = client['menu']
content = menu['content']

# 1-4集合名称users_info用来存储用户信息
users_info = menu['users_info']
# 集合名称users_content用来存储用户的数据
users_content = menu['users_content']
# 菜谱
menu_info = menu['menu_info']
# 评论
all_discuss = menu['all_discuss']


# 1-5 点击 http://127.0.0.1:5000/ 跳转到美食汇的首页

@app.route('/')
def menu():
    if session.get('logined'):
        user = session.get('username')
        page_number = 8
        pg1 = menu_info.find().count() // page_number
        pg = []
        for i in range(pg1):
            pg.append(i + 1)
        x1 = menu_info.find({}).limit(8)
        return render_template('menu.html', user=user, x1=x1, pp=1, pn=2, pg=pg, page_index=1)
    else:
        x1 = menu_info.find({}).limit(4)
        return render_template('menu.html', x1=x1, pg=[1])


# 分页
@app.route("/menu/<int:page_index>")
def page(page_index):
    if session.get('logined'):
        user = session.get('username')
        page_number = 8
        pg1 = menu_info.find().count() // page_number + 1
        pg = []
        for i in range(pg1):
            pg.append(i + 1)
        skip_num = (page_index - 1) * page_number
        x1 = menu_info.find().skip(skip_num).limit(page_number)
        pp = page_index - 1
        pn = page_index + 1
        if pp == 0:
            pp = 1
        if pn == 8:
            pn = 7
        return render_template("menu.html", user=user, x1=x1, pi=page_index, pg=pg, pp=pp, pn=pn)
    else:
        return render_template('login.html')


# 管理
@app.route('/usermanger')
def UserManger():
    if session.get('logined'):
        user = session.get('username')
        x1 = menu_info.find({"用户": user})
        return render_template('usermanger.html', x1=x1, user=user)
    else:
        return render_template('login.html')


# 详情
@app.route('/recipe/<page_index>')
def recipe(page_index):
    myquery = {"_id": ObjectId(page_index)}
    x2 = menu_info.find(myquery)
    user = session.get('username')
    return render_template("recipe.html", x2=x2, user=user)


# 发布文章
@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if request.method == 'GET':
        if session.get('logined'):
            user = session.get('username')
            return render_template('insert.html', user=user)
        else:
            return render_template('login.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        introduce = request.form.get('introduce')
        picURL = request.form.get('picURL')
        ingredient = request.form.get('ingredient')
        practice = request.form.get('practice')
        user = session.get('username')
        Tweet = {
            '用户': user,
            '标题': title,
            '介绍': introduce,
            '图片链接': picURL,
            '材料': ingredient,
            '做法': practice
        }
        menu_info.insert_one(Tweet)
        return render_template('insert.html', user=user)


# 修改文章
@app.route('/update/<page_index>', methods=['GET', 'POST'])
def update(page_index):
    if request.method == 'GET':
        if session.get('logined'):
            user = session.get('username')
            myquery = {"_id": ObjectId(page_index)}
            x2 = menu_info.find(myquery)
            for x1 in x2:
                x3 = x1
            return render_template('update.html', x3=x3, user=user)
        else:
            return render_template('login.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        introduce = request.form.get('introduce')
        picURL = request.form.get('picURL')
        ingredient = request.form.get('ingredient')
        practice = request.form.get('practice')
        Tweet = {
            '标题': title,
            '介绍': introduce,
            '图片链接': picURL,
            '材料': ingredient,
            '做法': practice
        }
        menu_info.update_many({'_id': ObjectId(page_index)}, {"$set": Tweet})
        return render_template('update.html')


# 1-5-1 删除路由
@app.route('/delete/<page_index>')
def delete(page_index):
    menu_info.delete_one({"_id": ObjectId(page_index)})
    user = session.get('username')
    x1 = menu_info.find({"用户": user})
    return render_template('usermanger.html', x1=x1, user=user)


# 1-6 注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    # 注册分两种请求,get请求表示从首页访问,然后跳转到注册页面
    if request.method == 'GET':
        return render_template('register.html')
    # 如果是post请求,则说明这个请求是一个注册请求,进行注册操作
    elif request.method == 'POST':
        success = False
        # 获取表单中的用户名和密码
        # 表单中用户名密码的键由前端的表单元素的name属性决定
        username = request.form.get('username')
        password = request.form.get('password')
        # 判断用户名和密码是否为空
        if len(username) < 3 or len(username) > 10 or len(password) < 8 or len(password) > 20:
            # 如果用户名或密码长度不符合,则跳转到注册页面并提示用户
            return render_template('register.html', success=False, info='用户名长度不可小于3个字或大于10个字,密码长度不可小于8个字或大于20个字,请重新输入')
        # 1.判断用户名是否已经存在
        if users_info.count_documents({'username': username}) == 0:
            # 2.用户名不存在,则将数据插入到数据库中
            data = {
                'username': username,
                'password': password
            }
            users_info.insert_one(data)
            # 3.跳转到登录界面并提示用户登录(success表示注册成功,info就是提示语句)
            return render_template('login.html', success=True, info='注册成功')
        else:
            # 2.用户名存在,跳转到注册页面并提示用户
            return render_template('register.html', success=False, info='注册失败')


# 1-7 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 登录操作记得维持登录状态,维持登录状态需要借助session
    # session本质上是一个字典
    # 使用session维持登录状态的步骤如下:
    # 1.从flask里面导入session(from flask import session)
    # 2.处于安全考虑,使用session必须配置密钥(app.config['SECRET_KEY'] = 密钥)
    # 3.往session里面存一个键值对,用于判断登录状态(session['logined_in'] = True)
    # session['logined_in'] = True
    # return redirect('/')

    # 判断请求的方法
    if request.method == 'GET':
        # 如果是get请求,说明是首页跳转过来登录的
        if session.get('logined'):
            # 如果用户已经登录,跳转到首页
            return redirect('/')
        else:
            # 如果用户还没有登录,跳转到登录页面
            return render_template('login.html')
    else:
        # 如果是post请求,说明这个请求是一个登录请求
        # 1.获取用户名和密码
        username = request.form.get('username')
        password = request.form.get('password')
        # 2.校验用户名密码是否为空
        if username == '':
            # 用户名为空,跳转到登录页面并提示用户用户名为空
            return render_template('login.html', success=False, info='用户名为空,请重新输入')
        elif password == '':
            # 密码为空,跳转到登录页面并提示用户密码为空
            return render_template('login.html', success=False, info='密码为空,请重新输入')
            # 3.判断用户是否存在
        if users_info.count_documents({'username': username}):
            # 用户存在
            # 判断密码是否正确
            # if users_info.find_one({'username': username}).get('password') == password:
            if users_info.find({'username': username})[0].get('password') == password:
                # 4.维持登录状态
                # 保存登录状态,用于后面判断是否已经登录
                session['logined'] = True
                # 保存用户名,用于后面获取用户数据时提供用户名
                session['username'] = request.form.get('username')
                # 5.跳转到首页
                return redirect('/')
            else:
                # 密码错误,跳转到登录页面并提示用户密码错误
                return render_template('login.html', success=False, info='密码错误,请重新登录')
        else:
            # 用户名不存在,跳转到登录页面并提示用户用户名不存在
            return render_template('register.html', success=False, info='用户名不存在,请重新注册')


# 1-6 修改密码路由
@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    # 注册分两种请求,get请求表示从首页访问,然后跳转到注册页面
    if request.method == 'GET':
        user = session.get('username')
        return render_template('changepassword.html', user=user)
    # 如果是post请求,则说明这个请求是一个注册请求,进行注册操作
    elif request.method == 'POST':
        success = False
        # 获取表单中的用户名和密码
        # 表单中用户名密码的键由前端的表单元素的name属性决定
        username = session.get('username')
        last_password = request.form.get('last_password')
        password = request.form.get('password')
        x = users_info.find({'username': '123'})
        for pw1 in x:
            pw2 = pw1['password']
        # 判断用户名和密码是否为空
        if len(password) < 8 or len(password) > 20:
            # 如果密码为空,则跳转到注册页面并提示用户
            return render_template('register.html', success=False, info='密码长度不可小于8个字或大于20个字,请重新输入')
        elif pw2 != last_password:
            return render_template('register.html', success=False, info='原密码错误')
        elif pw2 == password:
            return render_template('register.html', success=False, info='原密码与您输入的密码相同')
        else:
            data = {"$set": {
                'username': username,
                'password': password}
            }
            users_info.update_one({'username': username}, data)
            # 3.跳转到登录界面并提示用户登录(success表示注册成功,info就是提示语句)
            return render_template('login.html', success=True, info='修改成功')


# 1-7 注销路由
@app.route('/logout')
def logout():
    # 解除登录状态步骤
    # 1.将session里面的值清空
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    # 配置session所需要的密钥
    app.config['SECRET_KEY'] = 'root'
    app.debug = True
    app.run(host="0.0.0.0")
