## 常用指令

`git add`

把工作区的更改（新增、修改、删除的文件）放入 **暂存区（staging area）**。
 相当于说：“这些改动准备好提交了”。

------

`git commit`

把暂存区的内容保存为一个新的提交（commit），进入本地仓库历史。
 相当于说：“正式记录一次代码版本”。

- 每个提交都会有一个唯一的 **哈希值** 和 **提交信息**。

------

`git push`

把本地仓库中的提交 **推送到远程仓库**，让别人也能看到你做的更改。

- 一般会推到对应的远程分支，比如 `main` 或 `dev`。

------

总结顺序（常见工作流）：

1. 改代码
2. `git add 文件名` → 标记要提交的改动
3. `git commit -m "说明文字"` → 把改动保存到本地仓库
4. `git pull --rebase` → 先同步远程最新版本并把自己的提交放在后面
5. `git push` → 把自己的提交推送到远程



## 常见场景

### 1、第一次推送

第一次初始化项目并推送（提前在Github创建好项目）：

```bash
cd 你的笔记文件夹路径

# 初始化 Git 仓库
git init

# 添加远程仓库地址（替换成你自己的）
git remote add origin git@github.com:你的用户名/notes.git

# 添加所有文件并提交
git add .
git commit -m "Initial commit"

# 推送到 GitHub
git branch -M main
git push -u origin main
```



### 2、强制推送

强制推送（覆盖远程）

```bash
# 确保在本地仓库的 main 分支
git checkout main

# 把所有改动加到提交
git add .
git commit -m "重新上传所有笔记"

# 强制推送覆盖远程
git push -u origin main --force
```

如果想完全从零上传，可以直接删掉 `.git` 重新初始化：

```bash
# 在笔记文件夹下
rm -rf .git          # 删除旧的 Git 记录
git init             # 初始化新的仓库
git branch -M main   # 创建 main 分支
git remote add origin git@github.com:你的用户名/notes.git

git add .
git commit -m "初始提交（重新上传所有笔记）"
git push -u origin main
```



### 3、同一分支，不同User同时使用

------

场景1：电脑1没修改，电脑2修改并上传

- 电脑2：

  - 修改代码 → `git add . && git commit -m "xxx"` → `git push`

- 电脑1：

  - 直接更新即可：

    ```
    git pull origin main   # 假设分支是 main
    ```

  - 因为电脑1本地没改动，所以直接拉取不会冲突。

✅ 结果：电脑1与远程保持一致，获取到电脑2的修改。

------

场景2：电脑1修改并上传，电脑2修改了另一部分并上传

情况有两种：

- 修改的是完全不同的文件/代码位置（无冲突）

  - 电脑1先 `git push` 成功。

  - 电脑2再 `git push` 时，会提示 **推送被拒绝**（因为远程分支比本地新）。

  - 解决办法：

    ```
    git pull origin main   # 拉取并自动合并
    # 如果没冲突，会直接 merge
    git push               # 再推送到远程
    ```

- 修改了同一行或同一区域（有冲突）

  - 电脑2执行 `git pull` 时会提示冲突，需要手动编辑冲突文件，解决后：

    ```
    git add .
    git commit -m "resolve conflict"
    git push
    ```

✅ 最终：二者修改都能合并到远程。

------

场景3：电脑1执行了 `add` 和 `commit`，但是没 `push`，电脑2修改并上传了

- 当前情况：

  - 电脑1 本地有提交（未推送），落后远程
  - 电脑2 已经把修改推送到远程

- 解决方法：电脑1需要先把远程的更新合并进来：
   
  ```
  git pull --rebase origin main
  ```
  
  - `--rebase` 的作用：把电脑1本地提交，放到远程的提交之后，避免无意义的 merge commit。
  
- 然后再推送：

  ```
  git push origin main
  ```

⚠️ 如果有冲突，`git pull --rebase` 过程中会提示冲突，手动解决后继续：

```
git add .
git rebase --continue
```

✅ 最终：两台电脑的修改都在远程，历史更干净。

------

备注：

- `git pull` 的作用是 从远程仓库拉取最新的代码并合并到当前分支。默认情况下它会执行 `fetch + merge`，即把远程分支合并进来，可能会产生一个合并提交（merge commit）。
- `git pull --rebase` 则是 先拉取最新的远程分支，然后把本地的提交“挪到”最新远程提交之后。
   换句话说，它是 `fetch + rebase`，这样提交历史会更加线性、干净，不会产生多余的合并提交。

------

总结：

1. 无本地修改 → 直接 `git pull`。
2. 双方都修改 → 后 push 的人先 `git pull`（解决冲突后再 push）。
3. 本地已 commit 但没 push → 用 `git pull --rebase`，再 push。

------



## 常见报错

Q：上传时出现`Recv failure: Connection was reset`

A：https://zhuanlan.zhihu.com/p/648164862

需要为 Git 单独配置代理，可以使用以下命令

```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

配置完成后，可以使用以下命令查看并修改 Git 的配置：

```bash
git config --global --edit
```

如果仍然报错，可以检查代理端口是否配置正确，并尝试用以下命令设置关闭 SSL 证书验证：

```bash
git config --global http.sslVerify false
```

A：https://blog.csdn.net/qq_38415505/article/details/83687207

直接取消Git全局HTTP和HTTPS代理设置

```bash
git config --global --unset http.proxy 
git config --global --unset https.proxy
```

A：不用HTTP改用SSH

A：存在许多大文件，删除，或者借助一些工具处理一下

