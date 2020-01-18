# -*- coding: utf-8 -*-
from flask import Flask
from flask import jsonify
from flask import current_app

app = Flask(__name__)

# 激活上下文环境，可以绑定全局变量
ctx = app.app_context()
ctx.push()


import sqlite3
class Galdb(object):
    def __init__(self,dbpath='galgame.db'):
        self.dbpath = dbpath
        try:
            # 设置sqlite3不检查线程。因为sqlite3数据库默认同时只能有一个线程访问，这个app主要是读数据库，不会有冲突操作，所以取消掉也是安全的
            self.conn = sqlite3.connect(dbpath,check_same_thread=False)
            self.cursor =  self.conn.cursor()
        except Exception as e:
            raise ('connect database error,maybe given a wrong dbpath',e)

    def get_cv_rank(self,size='all'):
        self.cursor.execute('select * from cv_rank')
        if size == 'all':
            return self.cursor.fetchall()
        return self.cursor.fetchmany(size)
    def get_cv_game(self,id,size='all'):
        self.cursor.execute('select id,game.cover_url,game.maker,game.sales_day,game.title,game.official_website from  game  inner join (select game_id from "game-cv" where cv_id ='+str(id) + ') as gi on gi.game_id = game.id')
        if size == 'all':
            return self.cursor.fetchall()
        return self.cursor.fetchmany(size)


    def close(self):
        print('close dabebase connection...')
        self.cursor.close()
        self.conn.close()
        print('close succeed')

# current_app可以绑定当前应用的全局变量，在激活上下文后使用
current_app.galdb=Galdb()

@app.route("/api/cv_rank/<int:size>")
def cv_rank(size):
    cv_rank_list = current_app.galdb.get_cv_rank(size)
    print(cv_rank_list)
    return jsonify(cv_rank_list)

@app.route("/api/cv/<int:cv_id>")
def cv_detail(cv_id):
    cv_game_list = current_app.galdb.get_cv_game(cv_id,'all')
    print(cv_game_list)
    return jsonify(cv_game_list)

if __name__ =="__main__":
    app.run(host='0.0.0.0',port='3000',debug=True)
