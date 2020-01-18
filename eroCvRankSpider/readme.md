game 表
## id 主键
page_url
cover_path 封面图地址
cover_url 封面图路径
title
maker
sales_day
official_website
sales_page
is_deleted 删除标记
cv_table 外键 cv表
img_table 外键 图片列表
```
CREATE TABLE game (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    page_url         VARCHAR UNIQUE,
    cover_path       VARCHAR,
    cover_url        VARCHAR,
    title            VARCHAR,
    maker            VARCHAR,
    sales_day        VARCHAR,
    official_website VARCHAR,
    is_deleted       BOOLEAN,
    tmp1,
    tmp2,
    tmp3,
    tmp4,
    tmp5
);
```
## game-cv表
id  主键
character_name 角色名
cv_name cv名字
```angular2html
CREATE TABLE [game-cv] (
    id             INTEGER       PRIMARY KEY AUTOINCREMENT,
    character_name VARCHAR (255),
    cv_name        VARCHAR (255),
    game_id        INTEGER       REFERENCES game (id),
    cv_id          INTEGER       REFERENCES cv (id),
    tmp2,
    tmp3
);

```

## game-img表
id 主键
imgurl
imgpath
```
CREATE TABLE [game-img] (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    imgurl   VARCHAR UNIQUE,
    img_path VARCHAR UNIQUE,
    game_id          REFERENCES game (id),
    tmp1,
    tmp2,
    tmp3,
    tmp4,
    tmp5
);
```

## cv表
存储cv的id和名字
'''
CREATE TABLE cv (
    id   INTEGER       PRIMARY KEY,
    name VARCHAR (255),
    tmp1,
    tmp2,
    tmp3,
    tmp4,
    tmp5
);

'''

## cv_rank view
select cv_name,count(game_id) as count  from "game-cv" group by cv_name order by count desc


