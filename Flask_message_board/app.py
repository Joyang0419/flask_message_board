from flask import Flask, render_template, request, flash, redirect, url_for, session, escape
import os
from flask_sqlalchemy import SQLAlchemy # 處理資料庫
from sqlalchemy import or_
from form import *
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_paginate import Pagination, get_page_parameter # 分頁
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

basedir = os.path.abspath((os.path.dirname(__file__)))
UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

db = SQLAlchemy(app)
from models import *

bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)
### setting ###
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "12345678"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
###

@app.route('/') # 主頁
def index():
### 分頁 ###
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    users = User.query.all()
    pagination = Pagination(page=page, per_page=3 ,total=len(users)-1, bs_version=4, search=search, record_name='users')
    pagination_users = User.query.filter(User.username != 'Anonymous').paginate(page=page, per_page=3) # 排除Anonymous
    pagination_users = pagination_users.items
    # 'page' is the default name of the page parameter, it can be customized
    # e.g. Pagination(page_parameter='p', ...)
    # or set PAGE_PARAMETER in config file
    # also likes page_parameter, you can customize for per_page_parameter
    # you can set PER_PAGE_PARAMETER in config file
    # e.g. Pagination(per_page_parameter='pp')
###
### 用戶登陸狀態 ###
    if 'account' in session:
        current_user = User.query.filter_by(account=session['account']).first()
    else:
        current_user = User.query.filter_by(username='Anonymous').first()

    title = '留言板-首頁'
    content = {'title': title, 'users': users, 'pagination_users': pagination_users, 'pagination': pagination,
               'current_user': current_user}
    return render_template('index.html', **content)

@app.route('/register', methods=['GET', 'POST']) # 註冊
def register():
    ### 用戶登陸狀態 ###
    if 'account' in session:
        current_user = User.query.filter_by(account=session['account']).first()
    else:
        current_user = User.query.filter_by(username='Anonymous').first()
    form = FormRegister()
    if form.validate_on_submit():
        user = User(
            account=form.account.data,
            username=form.username.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
# upload picture
        image = form.image.data
        filename_saving = form.account.data + '.jpg'
        filename = secure_filename(filename_saving)
        image.save(os.path.join(
            basedir, 'static/images', filename
        ))
        return redirect(url_for('index'))
    return render_template('register.html', form=form, current_user=current_user)

@app.route('/message/<userid>', methods=['GET', 'POST']) # 進入訊息頁面
def message(userid):
### 用戶登陸狀態 ###
    if 'account' in session:
        current_user = User.query.filter_by(account=session['account']).first()
    else:
        current_user = User.query.filter_by(username='Anonymous').first()
###
    owner = User.query.get(userid)
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            owner=owner.account,
            senter=current_user.account,
            message=form.message.data,
            pub_date=datetime.now())
        db.session.add(message)
        db.session.commit()
        return redirect(request.url)
    messages = Message.query.filter_by(owner = owner.account).order_by(Message.pub_date).all()
### 分頁 ###
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, per_page=4 ,total=len(messages), bs_version=4, search=search, record_name='messages')
    pagination_items = Message.query.filter_by(owner = owner.account).order_by(Message.pub_date.desc()).paginate(page=page, per_page=4)
    pagination_items = pagination_items.items

######
    content = {'owner': owner, 'form': form, 'messages': messages,
               'pagination': pagination, 'pagination_items': pagination_items,
               'current_user': current_user}
    return render_template('message.html', **content)

@app.route('/login', methods=['GET', 'POST']) # 登入
def login():
### 用戶登陸狀態 ###
    if 'account' in session:
        current_user = User.query.filter_by(account=session['account']).first()
    else:
        current_user = User.query.filter_by(username='Anonymous').first()
###
    form = FormLogin()
    if form.validate_on_submit():
        user = User.query.filter_by(account=form.account.data).first() #  當使用者按下login之後，先檢核帳號是否存在系統內。
        if user:
            if user.password ==form.password.data: #  當使用者存在資料庫內再核對密碼是否正確。
                next = request.args.get('next')        #  使用者登入之後，將使用者導回來源url。利用request來取得參數next
                session['account'] = form.account.data # 用session remember username
                return redirect(next or url_for('index'))
            else:
                #  如果密碼驗證錯誤，就顯示錯誤訊息。
                flash('Wrong Password')
        else:
            #  如果資料庫無此帳號，就顯示錯誤訊息。
            flash('Wrong account')
    return render_template('login.html', form=form, current_user=current_user)

@app.route('/logout') # 登出
def logout():
    # remove the username from the session if it's there
    session.pop('account', None)
    return redirect(url_for('index'))

@app.route('/message/delete/<message_id>') # 刪除留言
def delete_message(message_id):
### 用戶登陸狀態 ###
    if 'account' in session:
        current_user = User.query.filter_by(account=session['account']).first()
    else:
        current_user = User.query.filter_by(username='Anonymous').first()
###
### message only senter & owner can delete, Anonymous always no
    message = Message.query.get(message_id)
    if (current_user.username != 'Anonymous'):
        if message.owner == current_user.account:
            db.session.delete(message)
            db.session.commit()
            print('delete')
        elif message.senter == current_user.account:
            db.session.delete(message)
            db.session.commit()
            print('delete')
    return redirect(url_for('message', userid=message.owner_relationship.id))

@app.route('/message/<userid>/update/<messageid>', methods=['GET', 'POST']) # 修改留言
def update_message(userid, messageid):
### 用戶登陸狀態 ###
    if 'account' in session:
        current_user = User.query.filter_by(account=session['account']).first()
    else:
        current_user = User.query.filter_by(username='Anonymous').first()
###
    owner = User.query.get(userid)
    form = MessageForm()
    messages = Message.query.filter_by(owner = owner.account).order_by(Message.id.desc()).all()
### 分頁 ###
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, per_page=4 ,total=len(messages), bs_version=4, search=search, record_name='messages')
    pagination_items = Message.query.filter_by(owner = owner.account).order_by(Message.id.desc()).paginate(page=page, per_page=4)
    pagination_items = pagination_items.items

######

### 修改留言 ###
    message_update = Message.query.get(messageid)
    if current_user.username == "Anonymous" or current_user.account != message_update.senter:
        return redirect(url_for('message', userid=userid))
    if form.validate_on_submit() and message_update.senter == current_user.account:
        message_update.message = form.message.data
        message_update.pub_date = datetime.now()
        db.session.add(message_update)
        db.session.commit()
        return redirect(url_for('message', userid=userid))
###
    content = {'owner': owner, 'form': form, 'messages': messages,
               'pagination': pagination, 'pagination_items': pagination_items,
               'current_user': current_user, 'userid': userid, 'message_update': message_update}
    return render_template('update.html', **content)





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=200) # 開放自己的ip:port給外界登入。