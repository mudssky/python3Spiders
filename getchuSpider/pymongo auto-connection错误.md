pymongo auto connection错误



今天突然发现，原来写的getchu爬虫有bug，有两个参数的正则解析有问题，没能匹配到正确的列表导致数据不完整。

所以说又要重爬了，还好之前爬完没把下载的页面全删掉，特地压缩了备份在那里，所以现在只要直接从文件中解析就行了，少了从网站爬取的一步，速度会快很多。

然后我之前写的从文件解析的py文件，没多想，没有用多进程。

因为感觉数据是存在硬盘上的。开多进程，相当于多个程序同时读取不同位置的数据，就会像迅雷下载一样，磁盘繁忙。磁盘不擅长随机读写，所以效率可能反而更低

单进程最大的问题在于cpu利用率太低。磁盘利用率其实也很低，毕竟程序中大量的正则还是要花一些时间。



这次我想搞快点，所以就决定开多进程了。一方面也是想测试一下，是否和我的想法一致。

结果cpu占用很轻松就达到100%，磁盘占用也达到了30m/s，算是相当快的速度了。

用python的pool.map方法，自动根据你的cpu核心数生成了十几个进程。



但是跑着跑着老是出现一个异常，导致程序中断

```python


PyMongo auto-reconnecting... localhost:27017: [WinError 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次。

```

我寻思之前单进程连接的时候，倒是没碰到过这种问题。

总之我看到这条报错提示觉得应该就是他说的那样，两个进程使用了同一个套接字





查了下pymongo的官方文档，其实也没找到原因。

大意：

pymongo不是进程安全的，所以说多个进程不能同用一个mongoclient实例。

但是我这边应该是每个进程都是自己创建的实例，所以不是这个问题啊

## [Is PyMongo fork-safe?](http://api.mongodb.com/python/current/faq.html?highlight=multi#id3)

PyMongo is not fork-safe. Care must be taken when using instances of [`MongoClient`](http://api.mongodb.com/python/current/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient) with `fork()`. Specifically, instances of MongoClient must not be copied from a parent process to a child process. Instead, the parent process and each child process must create their own instances of MongoClient. Instances of MongoClient copied from the parent process have a high probability of deadlock in the child process due to the inherent incompatibilities between `fork()`, threads, and locks described [below](http://api.mongodb.com/python/current/faq.html?highlight=multi#pymongo-fork-safe-details). PyMongo will attempt to issue a warning if there is a chance of this deadlock occurring.

MongoClient spawns multiple threads to run background tasks such as monitoring connected servers. These threads share state that is protected by instances of `Lock`, which are themselves [not fork-safe](http://bugs.python.org/issue6721). The driver is therefore subject to the same limitations as any other multithreaded code that uses `Lock` (and mutexes in general). One of these limitations is that the locks become useless after `fork()`. During the fork, all locks are copied over to the child process in the same state as they were in the parent: if they were locked, the copied locks are also locked. The child created by `fork()`only has one thread, so any locks that were taken out by other threads in the parent will never be released in the child. The next time the child process attempts to acquire one of these locks, deadlock occurs.

For a long but interesting read about the problems of Python locks in multithreaded contexts with `fork()`, see <http://bugs.python.org/issue6721>.



## [Using PyMongo with Multiprocessing](http://api.mongodb.com/python/current/faq.html?highlight=multi#id22)[¶](http://api.mongodb.com/python/current/faq.html?highlight=multi#using-pymongo-with-multiprocessing)

On Unix systems the multiprocessing module spawns processes using `fork()`. Care must be taken when using instances of [`MongoClient`](http://api.mongodb.com/python/current/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient) with `fork()`. Specifically, instances of MongoClient must not be copied from a parent process to a child process. Instead, the parent process and each child process must create their own instances of MongoClient. For example:

```
# Each process creates its own instance of MongoClient.
def func():
    db = pymongo.MongoClient().mydb
    # Do something with db.

proc = multiprocessing.Process(target=func)
proc.start()
```

**Never do this**:

```
client = pymongo.MongoClient()

# Each child process attempts to copy a global MongoClient
# created in the parent process. Never do this.
def func():
  db = client.mydb
  # Do something with db.

proc = multiprocessing.Process(target=func)
proc.start()
```

Instances of MongoClient copied from the parent process have a high probability of deadlock in the child process due to [inherent incompatibilities between fork(), threads, and locks](http://api.mongodb.com/python/current/faq.html?highlight=multi#pymongo-fork-safe-details). PyMongo will attempt to issue a warning if there is a chance of this deadlock occurring.





每次碰到多进程的问题总要考虑加锁之类的问题，所以我这次也本能地这么想。

应该是因为多进程的竞争导致两个进程抢到了同一个socket，出现错误，触发pymongo的重连机制。

网上找了半天，唯一找到的可用解决方案是类似下面的。

```python
import functools
import pymongo
import logging

MAX_AUTO_RECONNECT_ATTEMPTS = 5

def graceful_auto_reconnect(mongo_op_func):
  """Gracefully handle a reconnection event."""
  @functools.wraps(mongo_op_func)
  def wrapper(*args, **kwargs):
    for attempt in range(MAX_AUTO_RECONNECT_ATTEMPTS):
      try:
        return mongo_op_func(*args, **kwargs)
      except pymongo.errors.AutoReconnect as e:
        wait_t = 0.5 * pow(2, attempt) # exponential back off
        logging.warning("PyMongo auto-reconnecting... %s. Waiting %.1f seconds.", str(e), wait_t)
        time.sleep(wait_t)

  return wrapper

```

是一个装饰器的函数，

虽然装饰器的语法很久没用过算是完全忘了，但是这个函数大致作用还是可以看出来的。

捕获了auto-connection错误，然后time.sleep()等待一段时间，pymongo就会继续重连的逻辑。

但是没有解决根本问题。报错依然报错。

程序运行一段时间，等待一段时间，运行效率很低。这样最多是保证数据不丢失而已，那我还不如不用多进程，单进程就没那么多事。



其实问题的原因两种可能：

1. 多进程竞争资源导致的问题
2. 多进程速度太快，mongodb服务器撑不住导致的。



支持一的理由是，通常每个套接字地址(协议/网络地址/端口)只允许使用一次。这样的错误，明显是两个进程使用了同一个socket的导致的

不过这个问题可能出现在客户端，也可能出现在服务端。

服务端如果不是立刻关闭socket连接，那么一次大量连接涌入，然后socket就不够用了

问题，我这边最多也就每秒几千连接而已。才解析了4000个页面就停了。



支持二的理由，爬虫的时候也是开了多进程，但是没有这个异常。

不过这也有可能是因为爬虫有网络请求速度太慢





感觉还是因为问题一，mongo的服务器不至于那么弱

知识水平有限，实在是没能解决这个问题，所以我最后还是用单进程解析的数据。

因为不懂内部实现啊，估计想要解决问题，至少要看懂源码的水平。



用node js做解析就没那么多破事了，毕竟只有单进程单线程。





附赠一个mongodb 数字字符串按数值大小进行排序的方法：

Collation(排序规则)包含的字段：

{
   locale: <string>,
   caseLevel: <boolean>,
   caseFirst: <string>,
   strength: <int>,
   numericOrdering: <boolean>,
   alternate: <string>,
   maxVariable: <string>,
   backwards: <boolean>

}

**说明**

1. 当使用`collation`时，字段`locale`必须要有值。
2. `numericOrdering`决定字符串是否按照数值来排序，默认为`false`；
3. `caseFirst`决定大小写谁排在前头，“upper”大写排在小写前头，“lower”小写排在大写的前头。

{getchu_id:-1} {locale:'zh',numericOrdering:true}，所以说是这两个条件



db.stock.find({}).collation({"locale": "zh", numericOrdering:true}).sort({要排序的字段:1})

