# Basic knowledge

#### npm & npx

npm 是“安装工具”，npx是“执行工具”。

| 比较点     | `npm`                                  | `npx`                          |
| ---------- | -------------------------------------- | ------------------------------ |
| 全称       | Node Package Manager                   | Node Package Runner (Executor) |
| 作用       | 安装包、管理依赖                       | 直接运行包或 CLI 工具          |
| 是否安装包 | 安装后使用（全局/本地）                | 不一定安装，仅临时运行         |
| 用途       | 安装依赖：`npm install xxx`            | 运行 CLI 工具：`npx xxx`       |
| 示例       | `npm install -g eslint`<br/>`eslint .` | `npx eslint .`（无需全局安装） |



`npm run dev` & `npm start`

| 命令            | 作用                                            | 什么时候用                         |
| --------------- | ----------------------------------------------- | ---------------------------------- |
| `npm run dev`   | 启动开发服务器，开启热更新（自动刷新）          | **开发阶段**，边写边看效果         |
| `npm run build` | 打包项目，生成生产环境的代码（通常在 `dist/`）  | **上线前**，构建成浏览器能用的文件 |
| `npm start`     | 通常用来启动**生产环境服务**（如 Node.js 服务） | **部署后**，线上服务器运行时       |

在使用 Vite 的项目中，通常：

```
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm start        # 启动构建后的预览服务（vite preview）
```

举个前端项目例子（如 Vite 或 React）：

1. `npm run dev`

- 会启动一个本地开发服务器（比如 `localhost:5173`）
- 支持热更新（HMR）
- 快速调试和开发用的

2. `npm run build`

- 打包你的代码为纯静态文件
- 去除调试信息、压缩代码
- 输出到 `/dist` 或 `/build` 文件夹

3. `npm start`

- 用于运行项目或后端服务



#### msw

📚概念：

- `msw` 全称是 **Mock Service Worker**，是前端开发中常用的一个**接口请求模拟库**，用于模拟 API 调用，常见于开发和测试阶段。

📌 作用：

- 拦截网络请求（如 `fetch`, `axios` 调用）。
- 返回你自己定义的 mock 数据，而不需要依赖真实后端。
- 用于：
  - 前端独立开发（后端未完成）。
  - 编写自动化测试（如 Playwright）。
  - 本地调试时确保数据稳定。

🛠 工作方式：

- 它使用 **Service Worker API**，在浏览器中注册一个代理脚本，这个脚本会拦截你发出的网络请求，并根据配置返回“假数据”。
- 在项目中，你通常会看到一个叫 `mocks/handlers.ts` 或类似目录，定义了拦截的 URL 和返回的内容。



# React

## 一、核心语法

参考：

- 速成：[React速成-核心语法](https://www.bilibili.com/video/BV1pF411m7wV)
- 官网：https://react.dev/learn



### 1、创建项目 - 两种方法

通过脚手架创建项目：

```
npx create-react-app 项目名
cd 项目名
npm start 启动项目
```



核心的两个文件：

- index.js：项目引入
- APP.js

组件的撰写分为函数式组件与类组件，现在常用前者



### 2、JSX核心语法

（1）两个注意点

注意点1：JSX同时只能返回一个根元素

注意点2：标签闭合



（2）插值功能



（3）条件渲染

- 常见渲染
- 列表渲染



（4）事件操作



（5）useState 状态管理

- 一般状态管理
- 对象形式的状态修改
- 数组形式的状态



APP.js示例代码:

```js
import logo from './logo.svg';
import './App.css';
import { Fragment, useState } from 'react';

function App() {
  const divContent = '标签内容'
  const dicTitle = '标签标题'

  const flag = true
  let divContent2 = ''
  if (flag) {
    divContent2 = <span>flag = true</span>  // 无需写字符串，JSX可直接渲染
  } 
  else {
    divContent2 = <p>flag = false</p>
  }

  // const list = ["xiao ming", "xiao li", "xiao mei"]
  // 推荐加上id
  const list = [
    {id:1, name:"xiao ming"}, 
    {id:2, name:"xiao li"}, 
    {id:3, name:"xiao mei"}
  ]
  const listContent = list.map(
    item => (
      // 此时面对同时有两个根元素，且因为使用空标签<>不能加上key，所以可以采用另一种方法，Fragment（写代码时，会自动引入）
      <Fragment>
        <li ket = {item.id}>{item.name}</li>
        <li>---------</li>
      </Fragment>
    )
  )

  function handleClick(){
    console.log('click the botton')
  }

  const [content, setContent] = useState('the default content of the tag')
  function handleClick2(){
    setContent('new content')
  }

  const [data, setData] = useState({
    title: 'default title',
    content: 'default content'
  })
  function handleClick3() {
    // 点击按钮，修改标题
    setData({
      // title: 'new title'  // 直接这样写，setData会直接换掉旧值，旧的有title和content两个属性，现在content直接没了，如何只修改title呢？
      // 方法1：所有属性全部重新一一赋值
      // title: 'new title',
      // content: 'new content'
      // 方法2：利用data
      ...data,  // 注意data写前面
      title: 'new title2'
    })
  }

  const [data2, setData2] = useState(
    [
      {id:1, name:"xiao ming"}, 
      {id:2, name:"xiao li"}, 
      {id:3, name:"xiao mei"}
    ]
  )
  const listData2 = data2.map(
    item => (
      <li key={item.id}>{item.name}</li>
    )
  )
  let id = 3
  function handleClick4(){
    // change the list
    setData2([
      ...data2,  // 注意是data2而非data
      {id: ++id, name: 'xiao hong'}
    ])
  }

  return (  // 括号不要省略，以免一些引用问题
    // JSX同时只能返回一个根元素，所以如下这种同时出现两个div就会报错，解决方式之一就是再套一层容器
    <>
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
        </header>
      </div>
      
      <div>
        123
      </div>

      {/* 插值示例操作 */}
      <div title={dicTitle}>
        {divContent}
      </div>

      {/* 条件渲染示例操作1：基础操作 */}
      <div title={dicTitle}>
          {divContent2}
      </div>

      {/* 条件渲染示例操作2：列表渲染 */}
      <ul>{listContent}</ul>

      {/* 事件处理示例 */}
      <button onClick={handleClick}>button_demo</button>

      {/* 状态管理示例 */}
      <div>{content}</div>
      <button onClick={handleClick2}>button_demo2</button>

      {/* 状态管理示例2： 表格 */}
      <ul>{listData2}</ul>
      <button onClick={handleClick4}>button3</button>
    </>
  );
}

export default App;

```



## 二、组件通信与插槽

TODO



## 三、React Hooks 速成

TODO



## 四、React + TypeScript 综合案例

创建项目：

```
npx create-next-app@latest
cd 项目名
npm run dev
```

其中的参数：略



# React + Vite

TODO