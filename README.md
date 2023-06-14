# README

# 一、概述

![Frame215.jpg](README/volumn_04_light2.jpg)

项目基于：**基于稀疏网格的窄带拓扑优化**

**Narrow-Band Topology Optimization on a Sparsely Populated Grid**, ACM Transactions on Graphics (SIGGRAPH Asia 2018).

[[Paper]](https://yuanming.taichi.graphics/publication/2018-narrowband-topopt/) [[Video]](https://www.youtube.com/watch?v=H2OxHdQEQCQ)

原始项目链接：[https://github.com/yuanming-hu/spgrid_topo_opt](https://github.com/yuanming-hu/spgrid_topo_opt)

本项目为个人项目使用，在原项目的基础上
- 提供了安装流程引导
- 修复了若干原代码中的bug
- 提供一些后处理工具

# 二、安装

项目系统环境为**Ubuntu18.04 python3.8**

相关中文博客：

[基于稀疏网格的窄带拓扑优化（www.longlong.asia）](https://www.longlong.asia/2022/11/08/narrow-band-topology-optimization.html)

### 1. 配置icc环境

运行环境的核心是编译legacy版本的taichi和代码中附带的一个SPGrid求解器，其用到了Intel编译器和MKL的一些特性，为此还需要安装Intel Parallel Studio Xe

目前Intel的官网已经找不到Intel Parallel Studio Xe的下载地址，取而代之的是Intel oneAPI，经测试二者并不能兼容。Ubuntu18.04环境下，项目需要2019版本的Intel Parallel Studio Xe。

下载地址：[http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/15809/parallel_studio_xe_2019_update5_cluster_edition.tgz](http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/15809/parallel_studio_xe_2019_update5_cluster_edition.tgz)

其为商业版需要Intel提供的序列号或是证书文件。

备用链接（含证书文件）：[https://pan.baidu.com/s/1f_rrqspSCAIn-VuyVv6ecg](https://pan.baidu.com/s/1f_rrqspSCAIn-VuyVv6ecg) 提取码：0bwy

创建存储目录

`mkdir /hy-tmp`  （使用该名称是因为最开始调试该项目时使用了恒源云GPU平台，因此后面便沿用了下来，您可修改为任意地址，但注意后面代码中出现的任何相关地址都需要被替换）

`cd /hy-tmp` 进入目录

下载parallel_studio_xe_2019_update5_cluster_edition

`wget http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/15809/parallel_studio_xe_2019_update5_cluster_edition.tgz`


解压文件

`tar -zxvf parallel_studio_xe_2019_update5_cluster_edition.tgz`

把解压后得到的parallel_studio_xe_2019_update5_cluster_edition文件夹重命名为`ps`方便后续操作

`sudo mv parallel_studio_xe_2019_update5_cluster_edition/ ps/`

安装必要的库

`sudo apt update`

`sudo apt-get install cpio`

`sudo apt-get install xorg`

`sudo apt-get install libasound2-dev`

`sudo apt-get install libgtk2.0-dev`

`sudo apt-get install -y unzip`

`sudo apt-get install zip`

`sudo apt-get install libtbb2`

安装parallel_studio_xe_2019

`cd ps && ./install.sh`

- 安装过程
    
    
    一路回车，接受使用条款
    
    2 I do NOT consent to the collection of my Information
    
    `1`. Skip prerequisites [ default ]
    
    `2`. Activate with license file, or with Intel(R) Software License Manager
    
    `1`. Activate offline using a license file [ default ]
    
    下载证书文件 并上传至/hy-tmp/
    
    Please type the full path to your license file(s):
    
    `/hy-tmp/parallel_studio_b.lic`
    
    Activation completed successfully.
    
    Enter
    
    1. Finish configuring installation target [ default ]
    
    1. Accept configuration and begin installation [ default ]
    
    - 32-bit libraries not found
    
    1. Skip prerequisites [ default ]
    
    开始安装，耐心等待，大约会占用20G的空间
    
    ![Untitled](README%20d21396ef5b7a4e73b43ebca88c5c96bf/Untitled%201.png)
    

安装完后，**配置环境变量**

`cd /opt/intel`

`touch intel2019u5.sh`

`vim intel2019u5.sh`

按i键进入insert模式

加入以下内容

```jsx
*source* /opt/intel/compilers_and_libraries/linux/bin/compilervars.sh intel64
source /opt/intel/mkl/bin/mklvars.sh intel64
source /opt/intel/impi/2019.5.281/intel64/bin/mpivars.sh
```

键盘按 esc  输入 `:wq` 保存

接着`source /opt/intel/intel2019u5.sh`

即可设置好环境变量

把source /opt/intel/intel2019u5.sh加入~/.bashrc文件里，用户登录后即可生效。

**安装其他必要的库**

`sudo apt install mesa-common-dev`

`sudo apt install libglu1-mesa-dev freeglut3-dev`

`sudo apt-get install libnlopt-dev`

**安装 python环境3.8**

`sudo apt install python3.8`

`sudo apt install python3.8-dev`

创建软连接：

`sudo ln -fs /usr/bin/python3.8 /usr/bin/python3`

安装pip3

`sudo apt install python3-pip`

查看pip3是否指向了python3.8

`pip3 -V`

`pip3 install cython`

`pip3 install numpy==1.22`

`pip3 install pillow==8.0`

`pip3 install scipy==1.7`

`pip3 install flask`

`pip3 install PyQt5==5.14`

`pip3 install tqdm`

`pip3 install npyscreen`

### 2. 下载并编译taichi

`cd /hy-tmp`

**下载并安装taichi legacy**

`wget https://raw.githubusercontent.com/yuanming-hu/taichi/legacy/install.py`

`python3 install.py`

若出现网络原因导致的失败，需要多试几次

安装完成后`sudo -i`

`source ~/.bashrc`


**将项目放置于taichi-projects文件夹下**

`cd /hy-tmp/taichi/projects`

- 使用原版代码的情况：
    
    `git clone https://github.com/yuanming-hu/spgrid_topo_opt.git`
    
    将spgrid_topo_opt文件夹改名为spgrid:
    
    `sudo mv spgrid_topo_opt/ spgrid/`
    
    **修改**SPGrid_SIMD_Utilities**文件：**
    
    `cd /hy-tmp/taichi/projects/spgrid/external/SPGrid/Tools/`
    
    `vim SPGrid_SIMD_Utilities.h`
    
    修改文件SPGrid_SIMD_Utilities.h，在其include部分增加
    
    `#include <immintrin.h>`
    
    修改后 esc :wq 保存退出
    

- 或使用本项目修改后的代码
    
    `git clone https://github.com/Jeremyfff/spgrid.git`
    

**编译solver：**

`cd /hy-tmp/taichi/projects/spgrid/solver/`

`make`

等待编译完成

**编译其余部分**

`cd /hy-tmp/taichi/projects/spgrid/`

编译前需要先查询对应GPU的CUDA-ARCH

[https://developer.nvidia.com/cuda-gpus#collapseOne](https://developer.nvidia.com/cuda-gpus#collapseOne)

没有CUDA为0，根据查询到的CUDA架构修改下方的CUDA_ARCH 

```
export TC_MKL_PATH=/opt/intel/compilers_and_libraries_2019/linux/mkl/lib/intel64_lin/
export CUDA_ARCH=0
export TC_USE_DOUBLE=1
```

`ti build`

出现 Built target taichi_topo_opt 表明编译成功

遇到permission denied问题，`su root`

`chmod +x /hy-tmp/taichi/bin/ti`

# 三、 **运行示例文件**

### **3.1 常规方法：**

`cd /hy-tmp/taichi/projects/spgrid/scripts`

- 修改分辨率
    
    `vim opt_bridge.py`
    
    修改n = 1800 为 n = 300
    

`python3 opt_bridge.py`

※注意：遇到 libtbbmalloc.so.2: cannot open shared object file: No such file or directory 问题 是因为开机后没有运行以下指令`source /opt/intel/intel2019u5.sh`

后台运行：

`nohup python3 opt_bridge.py &`

### **3.2 使用本项目提供的帮助工具：**

※ 使用helper.py运行与查看结果：

`cd /hy-tmp/taichi/projects/spgrid/scripts/utils`

`python3 helper.py`

![Untitled](README/Untitled%202.png)

选择`1. Start a new solver`

![Untitled](README/Untitled%203.png)

nohup: 是否后台运行

要停止任务，在主菜单选择`2. Stop solver` ，选择正在运行的任务。

查看当前进度，在主菜单选择`3. Manage Solvers` 选择当前正在运行的任务

# 4. **查看运行结果**

### **4.1 常规方法：**

运行结果保存在`taichi/outputs/`目录下

`cd /hy-tmp/taichi/outputs/topo_opt/`

`ti run convert_fem_solve yourfilename --with-density`

遇到permission denied问题，`su root`

`chmod +x /hy-tmp/taichi/bin/ti`

生成密度场

```
# Without density field
ti run convert_fem_solve 00002.tcb
# With density field (can be huge)
ti run convert_fem_solve 00002.tcb --with-density
```

### 4.2 使用本项目提供的工具

`cd /hy-tmp/taichi/projects/spgrid/scripts/utils`

`python3 helper.py`

在主菜单选择`3. Manage Solvers` 选择当前正在运行的任务

![Untitled](README/Untitled%204.png)

选择Process

![Untitled](README/Untitled%205.png)

Target，处理文件的目标，一般选择为压缩后的ply.zip文件

Select File： All所有文件  Last最后一项 Custom idx 自定义序号

自定义序号使用英文逗号分割，支持范围输入，如图所示

Threads 线程数。根据文件大小，每个线程会占用一定的内存空间，请勿在不知道每个线程会占用多少空间的情况下就把线程开的很多。

下面按钮中，Porcess(nohup)已弃用，选择Process后会在主界面实时显示处理进度

处理完成后，下载至本地计算机并进一步预览：

[使用[spgrid/](https://github.com/Jeremyfff/spgrid/tree/main)**scripts/local/auto_download_gui.py自动下载到本地文件夹](README%20d21396ef5b7a4e73b43ebca88c5c96bf/%E4%BD%BF%E7%94%A8spgrid%20scripts%20local%20auto_download_gui%20py%E8%87%AA%E5%8A%A8%E4%B8%8B%E8%BD%BD%E5%88%B0%E6%9C%AC%E5%9C%B0%20026988fdc4114c48b9631836ca632055.md)