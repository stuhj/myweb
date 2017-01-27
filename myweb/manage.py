#encoding=UTF-8


from web import app,db
from web.models import User,Image,Comment
import random
from sqlalchemy import or_,and_
from flask_script import Manager

import sys
reload(sys)
sys.setdefaultencoding('utf8')

manager = Manager(app)


def get_image_url():
    return 'http://wx2.sinaimg.cn/mw690/bf528b0fly1fbx6tipengj20qo0zkkjl.jpg'#'http://images.nowcoder.com/head/'+str(random.randint(3,5))+'m.png'





@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0,100):
        db.session.add(User(str(i+1),'aaa'))
        for j in range(0,10):
            db.session.add(Image(get_image_url(),i+1))
            for k in range(0,random.randint(1,4)):
                db.session.add(Comment(10*i+j+1,i+1,'This is a Comment'+str(k)))
    db.session.commit()


   # print 1, User.query.all()   #查询
    #print 2,User.query.order_by(User.id.desc()).limit(2).all()
 #   print 3, User.query.filter_by(id=5).first()
  #  print 4, User.query.filter(or_(User.id == 10,User.id == 99)).all()

'''
    for m in range(1,10,2):
        user=User.query.get(m)
        user.username = 'NEW'+user.username

    for n in range(50,80,2):
        comment = Comment.query.get(n)
        db.session.delete(comment)
 '''
    

@manager.command
def delete():
    images=Image.query.filter_by(user_id=101).all()

    for i in images:
        db.session.delete(i)
        db.session.commit()

if __name__ == '__main__':
    manager.run()
