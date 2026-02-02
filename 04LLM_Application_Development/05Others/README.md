> 参考：[告别JSON冗余：TOON让Token成本降低30-60%](https://mp.weixin.qq.com/s/9ibJgKUwCBogb6Gho69Zhg)

Python实现的`python-toon`库让我们能轻松在Python生态中使用这种高效格式。

直观对比Json与TOON：

- json格式：177字符

  ```
  {"users": [{"id": 1, "name": "Alice", "age": 30, "active": true}, {"id": 2, "name": "Bob", "age": 25, "active": true}, {"id": 3, "name": "Charlie", "age": 35, "active": false}]}
  ```

- TOON格式：85字符

  ```
  users[3,]{id,name,age,active}:
    1,Alice,30,true
    2,Bob,25,true
    3,Charlie,35,false
  ```

关键是后续模型支持的力度咋样，json目前肯定都会训练进去，TOON是否会被主流模型跟进？