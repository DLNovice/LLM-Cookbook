内容概述：

- 了解CPU的拓扑结构等信息：如AMD的EPYC系列芯片（官网下载文档）
- 基于numactl等方法限制核心：参考附属文档
- 超线程（SMT）修改方法：参考下文



### **关闭超线程（SMT）步骤**

---

#### **1. 确认当前SMT状态**
在操作前，检查系统是否启用了超线程（SMT）：
```bash
lscpu | grep "Thread(s) per core"
```
- 输出为 `Thread(s) per core: 1` 表示 **未启用** SMT。
- 输出为 `Thread(s) per core: 2` 表示 **已启用** SMT。

或直接查看内核参数文件：
```bash
cat /sys/devices/system/cpu/smt/active
```
- 输出 `1` 表示已启用，`0` 表示禁用。

---

#### **2. 暂时关闭SMT**
可以通过 `sysfs` 接口动态关闭，**重启后失效**：
```bash
echo off | sudo tee /sys/devices/system/cpu/smt/control
```
验证是否生效：
```bash
cat /sys/devices/system/cpu/smt/active        # 应输出 0
lscpu | grep "Thread(s) per core"             # 应显示 1
```

---

#### **3. 永久关闭SMT**
通过添加内核启动参数，使系统每次启动时禁用SMT：

##### **步骤1：修改GRUB配置**
编辑 `/etc/default/grub` 文件：
```bash
sudo vim /etc/default/grub
```
在 `GRUB_CMDLINE_LINUX` 行中添加 `nosmt` 参数：
```bash
GRUB_CMDLINE_LINUX="... nosmt"  # 保持原有参数，并追加 nosmt
```

##### **步骤2：更新GRUB并重启**
更新配置（根据系统类型选择命令）：
```bash
sudo update-grub          # Ubuntu/Debian
sudo grub2-mkconfig -o /boot/grub2/grub.cfg  # RHEL/CentOS
```
重启系统：
```bash
sudo reboot
```

##### **步骤3：验证永久生效**
重启后检查：
```bash
cat /sys/devices/system/cpu/smt/active  # 应显示 0
lscpu | grep "Thread(s) per core"       # 应显示 Thread(s) per core: 1
```

---

#### **4. （可选）通过BIOS禁用SMT**
如果需要在硬件层面完全关闭SMT，需进入服务器的BIOS设置：
1. 重启服务器，按 `DEL` 或 `F2` 进入BIOS（具体按键取决于厂商）。
2. 找到 `Advanced CPU Configuration` 或类似菜单。
3. 关闭选项 `Simultaneous Multithreading (SMT)` 或 `Hyper-Threading`。
4. 保存退出并重启。

---

#### **5. 补充说明**
- **兼容性**：`nosmt` 参数支持Linux内核 >=4.11，绝大多数现代发行版均可使用。
- **AMD与Intel差异**：AMD平台的内核参数 `nosmt` 和 `smt=off` 是等效的；Intel平台参数为 `noht`（较少使用，通常直接 `nosmt`）。
- **性能影响**：关闭SMT会减少逻辑CPU数量，可能影响多线程任务性能，但能减少资源竞争（适合延迟敏感型任务）。

---

**总结**：  
根据需求选择临时或永久关闭SMT。若测试环境下需要快速操作，使用 `sysfs` 动态关闭；若需持久生效，修改GRUB参数重启即可。对于物理服务器，建议在BIOS中彻底禁用以确保所有层级生效。