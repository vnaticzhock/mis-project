import os
from pathlib import Path
import pandas as pd
import psycopg2
from tqdm import tqdm
from dbhelper import dbhelper

# 將餐廳位置映射到 index
files = os.listdir('./raw_data/')
mapper = {k.split('.')[0]: v for v, k in enumerate(files)}

# 連接 postgres
db = dbhelper()
conn = db.conn
cursor = db.cursor

print('initializing db...')
cursor.execute('DROP TABLE IF EXISTS comments;')
cursor.execute(
    'CREATE TABLE comments (rest_index INTEGER, user_id CHAR(21), rating REAL, comment_text VARCHAR(400));')
cursor.execute(
    'ALTER TABLE comments ADD CONSTRAINT "rest_user" PRIMARY KEY(rest_index, user_id);')

print('iterate files...')
for file in tqdm(files):
    df = pd.read_csv(Path('./raw_data/') / file)
    df = df[df['local_guide'] == True]

    user_id = df['user_profile_url'].map(lambda x: x.split('/')[5]).to_list()
    rating = df['rating'].to_list()
    comment_text = df['comment_text'].to_list()

    assert len(user_id) == len(rating) and len(rating) == len(comment_text)

    sort = [(rest_index, x, y, z)
            for rest_index, (x, y, z) in zip([mapper[file.split('.')[0]]] * len(user_id), sorted(zip(user_id, rating, comment_text)))]

    # 寫進資料庫裡, 供等等建立 index, 方便二元查詢
    for index, i, j, k in sort:
        k = k.strip(' ').replace('\n', ' ')
        k = "，".join(k.split(' '))
        cursor.execute("INSERT INTO comments (rest_index, user_id, rating, comment_text) VALUES (%s, %s, %s, %s);",
                       (str(index), i, j, k))

# 建立 index
cursor.execute('CREATE INDEX "rest" ON comments (rest_index);')
cursor.execute('CREATE INDEX "user" ON comments (user_id);')

conn.commit()
cursor.close()
conn.close()
