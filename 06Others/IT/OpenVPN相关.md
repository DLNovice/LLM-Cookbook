参考教程：

- https://www.meowpass.com/pages/d2b60b/#_1-%E5%89%8D%E8%A8%80
- https://www.77bx.com/325.html
- https://juejin.cn/post/7503462035272777778



# OpenVPN安装

## 方法一：docker安装

docker安装不可用，无论是第三方封装的docker compose还是官方的docker安装方案，首先启动时会出现端口冲突问题（与dify等项目存在冲突），web ui、tcp、udp三个接口均改为高端口，docker容器可正常启动，但是无法使用，查看日志发现报错：`builtins.AttributeError:" _Code" object has no attribute 'co_positions'`。

暂未解决。



## 方法二：直接安装openvpn connect

> 官网教程：https://openvpn.net/openvpn-client-for-linux/

（注意，下述全程提前su进入root权限）官方提供了`**Stable repository** - Debian / Ubuntu`安装方案：

1、安装依赖 Ensure you have the needed support packages already installed:

```
apt install apt-transport-https curl
```



2、Retrieve the OpenVPN Inc package signing key:

注意，普通用户权限不行，sudo也不行，root权限才行

```
mkdir -p /etc/apt/keyrings    ### This might not exist in all distributions
curl -sSfL https://packages.openvpn.net/packages-repo.gpg >/etc/apt/keyrings/openvpn.asc
```

上述正常是没有输出的，需要手动查一下才能找到DISTRIBUTION，比如

```
. /etc/os-release && echo "$VERSION_CODENAME"
```

例如：

- 输出为 `bookworm` ⇒ Debian 12
- 输出为 `bullseye` ⇒ Debian 11
- 输出为 `jammy` ⇒ Ubuntu 22.04
- 输出为 `focal` ⇒ Ubuntu 20.04

我当前Ubuntu 24.04输出为noble

（后续调试时貌似用的别的，多尝试几次，只要后续apt install openvpn3成功即可）



3、Replace the `DISTRIBUTION` part in the command below using the release name from the table above to set up the apt source listing:

```
echo "deb [signed-by=/etc/apt/keyrings/openvpn.asc] https://packages.openvpn.net/openvpn3/debian DISTRIBUTION main" >>/etc/apt/sources.list.d/openvpn3.list
```

主要是将上述DISTRIBUTION切换为别的



4、To install OpenVPN 3 Linux, run these commands:

下面两个安装指令也要root权限

```
apt update
apt install openvpn3
```

验证：

```
openvpn3 version
```



# 配置及启动

准备ovpn文件（根据需要修改配置），导入后启动即可（无需root权限，部分需要sudo权限）：

1、导入ovpn文件：`openvpn3 config-import --config /path/to/***.ovpn --persistent`

查看是否导入成功（什么权限导入的，就用什么权限查看）：`openvpn3 configs-list`

2、`root权限`启动（config后直接写已经导入后的ovpn文件名称即可）：`openvpn --config YYQ-Server2.ovpn`

------

其他注意事项：

1、第一次启动时提示`Options error: option 'route' cannot be used in this context ([PUSH-OPTIONS])`，所以删除了ovpn中route相关字段：

```
route-nopul1
route 10.7.7.0 255.255.255.0 vpn gateway
route 166.111.0.0 255.255.0.0 vpn gateway
```

报错解决

2、启动ovpn时需要sudo权限，否则

```
2025-07-03 16:57:12 ERROR: Cannot ioctl TUNSETIFF tunx: Operation not permitted (errno=1)
2025-07-03 16:57:12 Exiting due to fatal error
```

3、其次，账号密码最好还是手动输入一下，之前因为复制存在空格出现了：

```
2025-07-03 17:00:59 AUTH: Received control message: AUTH_FAILED
2025-07-03 17:00:59 SIGTERM[soft,auth-failure] received, process exiting
```

4、启动后并非立即可用，等待几分钟后，北京那边才可用

5、关于导入后的ovpn文件`sudo openvpn3 config-remove `无法删除的问题

实操发现，`openvpn3 configs-list`与`sudo openvpn3 configs-list`输出结果不同，这取决于当初导入config时是什么权限，但是，是否采用sudo，均无法删除已导入的ovpn文件，且导入同名文件并不冲突。

暂未解决，修改ovpn文件名称重新导入并使用，临时解决了问题。



# 开机自启动

> 开机自启动基于tmux挂载的OpenVPN服务

`vim /usr/local/bin/start_openvpn.sh`，注意，第一行不能少，即不能缺少 Shebang（首行指明解释器）

```
#!/bin/bash
cd /home/user/WorkSpace/OpenVPN
openvpn --config YYQ-Server2.ovpn
```

给脚本加上免密：

- 创建包含用户名和密码的文件：`sudo nano /etc/openvpn/credentials.txt`

- 修改 `.ovpn` 配置文件，添加或者修改这一行：

  ```
  auth-user-pass /etc/openvpn/credentials.txt
  ```

- 权限保护：

  ```
  sudo chmod 600 /etc/openvpn/credentials.txt
  ```


进入root权限，给脚本添加执行权限：`chmod +x /home/user/start_openvpn.sh`

撰写系统服务脚本：`sudo nano /etc/systemd/system/start_openvpn.service`

```
[Unit]
Description=Run custom script in tmux at boot
After=network.target

[Service]
Type=forking
User=root
ExecStart=/usr/bin/tmux new-session -d -s start_openvpn "/home/user/start_openvpn.sh"
ExecStop=/usr/bin/tmux kill-session -t start_openvpn
Restart=always

[Install]
WantedBy=multi-user.target
```

重新加载 systemd 并启用服务：

```
sudo systemctl daemon-reexec
sudo systemctl enable start_openvpn.service
sudo systemctl start start_openvpn.service


# 重新加载并启动服务
sudo systemctl daemon-reexec
sudo systemctl restart start_openvpn.service
```

查看是否启动成功：

```
sudo journalctl -u start_openvpn.service   # 查看日志

systemctl status start_openvpn.service  # 查看服务状态


su  # 先进入root权限，才能看到tmux会话是否开启
tmux ls         # 查看是否存在 myscript 会话
```

备注：

- 查看当前已经启动的服务：`systemctl list-units --type=service --state=running`
- 查看设置为“开机自启动”的服务：`systemctl list-unit-files --type=service --state=enabled`
- 查看所有服务（包括未运行的）：`systemctl list-units --type=service`