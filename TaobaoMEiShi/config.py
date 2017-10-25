DRIVER_PATH = r'C:\Users\cq_xuke\Downloads\phantomjs-2.1.1-windows\bin\phantomjs.exe'

CREATE_TABLE = '''
CREATE TABLE taobaopage (id BIGINT(7) NOT NULL AUTO_INCREMENT, name VARCHAR(200),
image VARCHAR(500), price VARCHAR(100), location VARCHAR(100), deal VARCHAR(100),
shop VARCHAR(100), created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(id));
'''
INSERT_DATA='''INSERT taobaopage (name,image,price,location,deal,shop) 
VALUES ("{0}","{1}","{2}","{3}","{4}","{5}")
'''

SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']

CONNECTION = dict(host='127.0.0.1', user='root', passwd='xk200900330022', db='mysql', charset="utf8")
