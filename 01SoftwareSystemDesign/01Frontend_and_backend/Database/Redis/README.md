概述：[redis是什么?架构是怎么样的？怎么设计redis？](https://www.bilibili.com/video/BV18jBiYpEDJ)

快速入门：[【GeekHour】一小时Redis教程](https://www.bilibili.com/video/BV1Jj411D7oG)

## 快速入门

### 安装

基于apt或者docker安装redis

redis-cli或者GUI工具使用Redis

GUI工具RedisInsigjht的使用



### 常用指令

#### 字符串String

基于SET设置键值对

GET查看值

存储是字符串，所以支持很多类型

DEL删除键值对

EXISTS判断键值对是否存在，返回1和0

基于KEYS查看有哪些键

FLUSHALL一键删除



REDIS键值对都是二进制存储的，默认不支持中文（换为二进制了），需要使用redis-cli --raw启动REDIS，就能正常显示中文了



TTL查看键的过期时间

EXPIRE设置过期时间

SETES设置带有过期时间的键值对

SETNX只有键不存在时才设置键的值



#### 列表List

LPUSH或者RPUSH将元素添加到列表头部和尾部

LPOP或者RPOP删除列表头部和尾部元素



#### 集合Set

SADD添加元素

SMEMBERS查看集合

SISMEMBRT判断值是否在集合中

SREM删除元素

SINTER、SUNION、SDIFF等做集合的运算



#### 有序集合SortedSet

和集合的区别为，其每个元素都会关联一个浮点类型的分数，按分数进行排序（分数可以重复）



ZADD添加元素

ZRANGE查看

CSCORE

等等



#### 哈希Hash

HSET设置哈希

等等



### 功能

#### 发布订阅模式

一个终端基于SUBSCRIBE订阅一个评到

一个终端基于PUBLISH发送信息

发布订阅模式有很多局限性



#### 消息队列Stream

阻塞



#### 地理空间Geospatial

REDIS3.2后的新特性，提供了一种存储地理位置信息的数据结构

计算操作



#### HyperLogLog

用来做基数统计的算法



#### 位图Bitmap

字符串类型的扩展

String模拟Bit

位运算



#### 位域Bitfield

记录玩家关键信息



#### 事务

在一次请求中执行多个命令

MULTI应用于开启一个事务，开启后所有命令会放入到一个队列中

通过EXEC/DISCARD



非原子操作（要么全部成功，要么全部失败）

某个命令执行失败，后面的命令依旧执行



#### 持久化

没有持久化，断电等情况下，缓存数据会消失。

两种方式

- RDB方式
- AOF方式



#### 主从复制

将一个REDIS（主）复制到另一个REDIS（从），一个主节点（单个），一个从节点（可多个）。

自动同步。



#### 哨兵模式

主节点宕机了是否可以自动将从节点设置为新的主节点，实现自动化/高可用？有的，兄弟有的。
