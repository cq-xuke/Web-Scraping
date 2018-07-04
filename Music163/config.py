DRIVER_PATH = r'C:\Users\cq_xuke\Downloads\phantomjs-2.1.1-windows\bin\phantomjs.exe'

CREATE_TABLE = '''
CREATE TABLE music163page (id BIGINT(7) NOT NULL AUTO_INCREMENT, song VARCHAR(200),
song_id VARCHAR(100), reviewer VARCHAR(100), reviewer_home VARCHAR(500), comment VARCHAR(1000),
likes VARCHAR(100), time VARCHAR(100), comment_nums VARCHAR(1000), created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(id));
'''
INSERT_DATA = '''INSERT music163page (song,song_id,reviewer,reviewer_home,comment,likes,time,comment_nums) 
VALUES ("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}");
'''

SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']

CONNECTION = dict(host='127.0.0.1', user='root', passwd='xk200900330022', db='mysql', charset="utf8")
