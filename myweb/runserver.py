#encoding=UTF-8

from web import app

import sys
reload(sys)
sys.setdefaultencoding('utf8')
if __name__ =='__main__':
    app.run(debug=True,port=8000)