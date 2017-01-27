# -*- coding: utf-8 -*-
# flake8: noqa
from web import app
from qiniu import Auth, put_file, etag, urlsafe_base64_encode,put_data,put_stream
import qiniu.config

#密钥太坑
access_key = 'M-sMZ4iG_BZow20GM7CiNrQt-Dpd8QksfrQ3rmmR'
secret_key = 'fRDdb-m7rGqxRLeymcso3lfHMaVCkOnXauWIzXXV'

q = Auth(access_key, secret_key)


bucket_name = app.config['QINIU_BUCKET_NAME']
domain_prefix = app.config['QINIU_DOMAIN']


def upload_to_qiniu(source_file,file_name):
    token = q.upload_token(bucket_name, file_name)
    print dir(source_file)
    #ret, info = put_data(token, file_name, source_file.stream)
    ret, info = put_data(token, file_name, source_file.stream)

    if info.status_code == 200:
        return domain_prefix+file_name
    else:
        return None
