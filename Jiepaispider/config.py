GROUP_START = 1
GROUP_END = 20
KEYWORDS = '街拍'

CREATE_TABLR = '''
CREATE TABLE ToutiaoPage (id BIGINT(7) NOT NULL AUTO_INCREMENT, title VARCHAR(200),
url VARCHAR(100), images VARCHAR(5000), created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY(id));
'''
INSERT_DATA='INSERT INTO ToutiaoPage (title,url,images) VALUES ("{0}","{1}","{2}")'

CONNECTION = dict(host='127.0.0.1', user='root', passwd='xk200900330022', db='mysql', charset="utf8")
