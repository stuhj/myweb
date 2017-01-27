#encoding=UTF-8

from web import app,db,login_manager
from models import User,Image,Comment
from flask import render_template,redirect,request,make_response,flash,get_flashed_messages,send_from_directory
from flask_login import  login_user,logout_user,current_user,login_required
import random,hashlib,json,uuid,os
from qiniusdk import upload_to_qiniu



#主页
@app.route('/')
def index():
    #images = Image.query.order_by(db.desc(Image.id)).limit(10).all()

    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=1,per_page=5,error_out=False)
    return render_template('index2.html',images=paginate.items,has_next=paginate.has_next)
    #return render_template('index2.html', images=images)

#图片详情页
@app.route('/image/<int:image_id>')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/',code=302)
    return render_template('pageDetail.html',image=image)

#个人页
@app.route('/profile/<int:user_id>/')
@login_required
def user(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/',code=302)
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1,per_page=3,error_out=False)
    return render_template('profile.html',user=user,images=paginate.items,has_next=paginate.has_next)

#后端为首页提供分页接口
@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page,per_page):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page,per_page=per_page,error_out=False)
    map={'has_next':paginate.has_next}
    images=[]
    for image in paginate.items:
        comments = []
        for i in range(0,min(2,len(image.comments))):
            comment = image.comments[i]
            comments.append({'content'+str(i):comment.content,
                            'username'+str(i):comment.user.username,
                             'user_id'+str(i):comment.user_id})
        num = len(comments)
        imagvo={'id':image.id,'url':image.url,
                 'comment_count':len(image.comments),
                 'head_url':image.user.head_url,
                 'user_id':image.user_id,
                 'created_date':str(image.created_date),
                 'comments_num':num
                 }
        for j in comments:
            for k,v in j.iteritems():
                imagvo[k] = v

        images.append(imagvo)

    map['images'] = images
    return json.dumps(map)

#后端为个人页提供分页AJAX接口
@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id,page,per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page,per_page=per_page,error_out=False)
    map={'has_next':paginate.has_next}
    images=[]
    for image in paginate.items:
        imgvo = {'id':image.id,'url':image.url,'comment_count':len(image.comments)}
        images.append(imgvo)

    map['images'] = images
    return json.dumps(map)



@app.route('/regloginpage',methods={'post','get'})
def regloginpage():
    msg=''
    for m in get_flashed_messages(with_categories=False,category_filter=['reglogin']):
        msg = msg + m
    return render_template('login.html',msg = msg,next=request.values.get('next'))






def redirect_with_msg(target,msg,category):
    if msg != None:
        flash(msg,category=category)
    return redirect(target)


@app.route('/reg',methods={'post','get'})
def reg():
    username=request.values.get('username').strip()
    password=request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage', u'用户名或密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user != None:
        return redirect_with_msg('/regloginpage',u'用户名已经存在','reglogin')


    salt = '.'.join(random.sample('123456789asdfghjASDFGHJ',10))
    m = hashlib.md5()
    m.update(password+salt)
    password = m.hexdigest()
    user = User(username,password,salt)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    print 111
    return redirect('/')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/login',methods={'post','get'})
def login():
    username=request.values.get('username').strip()
    password=request.values.get('password').strip()
    if username == '' or password == '':
        return redirect_with_msg('/regloginpage', u'用户名或密码不能为空', 'reglogin')
    user = User.query.filter_by(username=username).first()
    print username,password
    print user
    if user ==None:
        return redirect_with_msg('/regloginpage', u'用户名不存在', 'reglogin')
    m = hashlib.md5()
    m.update(password+user.salt)
    print user.password,m.hexdigest()
    if m.hexdigest() != user.password:
        return redirect_with_msg('/regloginpage', u'密码错误', 'reglogin')

    login_user(user)

    #自动跳转到next
    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')

def save_to_local(file,file_name):
    save_dir = app['UPLOAD_DIR']
    file.save(os.path.join(save_dir,file_name))
    return '/image/'+file_name

@app.route('/upload/',methods=['post'])
def upload():
    file = request.files['file']
    file_ext=''
    if file.filename.find('.')>0:
        file_ext = file.filename.rsplit('.',1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-','')+'.'+file_ext
        #url = save_to_local(file,file_name)
        print file_name
        url = upload_to_qiniu(file,file_name)

        if url != None:
            print url
            db.session.add(Image(url,current_user.id))
            db.session.commit()

    return redirect('/profile/%d' %current_user.id)


@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'],image_name)


#详情页评论
@app.route('/addcomment/',methods={'post'})
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content']
    comment = Comment(image_id,current_user.id,content)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code":0,"id":comment.id,"username":comment.user.username,
                       "user_id":current_user.id})
