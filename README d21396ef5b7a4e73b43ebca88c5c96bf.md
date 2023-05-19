# README

# 一、概述

![Frame215.jpg](README%20d21396ef5b7a4e73b43ebca88c5c96bf/Frame215.jpg)

项目基于：**基于稀疏网格的窄带拓扑优化**

**Narrow-Band Topology Optimization on a Sparsely Populated Grid**, ACM Transactions on Graphics (SIGGRAPH Asia 2018).

****[[Paper]](https://yuanming.taichi.graphics/publication/2018-narrowband-topopt/) [[Video]](https://www.youtube.com/watch?v=H2OxHdQEQCQ)**

原始项目链接：[https://github.com/yuanming-hu/spgrid_topo_opt](https://github.com/yuanming-hu/spgrid_topo_opt)

- 提供了安装流程引导
- 修复了若干原代码中的bug
- 提供一些后处理工具

# 二、安装

项目系统环境为**Ubuntu18.04 python3.8**

相关中文博客：

[基于稀疏网格的窄带拓扑优化](https://www.longlong.asia/2022/11/08/narrow-band-topology-optimization.html)

### 1. 配置icc环境

运行环境的核心是编译legacy版本的taichi和代码中附带的一个SPGrid求解器，其用到了Intel编译器和MKL的一些特性，为此还需要安装Intel Parallel Studio Xe

目前Intel的官网已经找不到Intel Parallel Studio Xe的下载地址，取而代之的是Intel oneAPI，经测试二者并不能兼容。Ubuntu18.04环境下，项目需要2019版本的Intel Parallel Studio Xe。

下载地址：[http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/15809/parallel_studio_xe_2019_update5_cluster_edition.tgz](http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/15809/parallel_studio_xe_2019_update5_cluster_edition.tgz)

其为商业版需要Intel提供的序列号或是证书文件。

[下载证书文件 ](README%20d21396ef5b7a4e73b43ebca88c5c96bf/%E4%B8%8B%E8%BD%BD%E8%AF%81%E4%B9%A6%E6%96%87%E4%BB%B6%20d9b071dff6e04869b957d9675ce15155.md)

创建存储目录

`mkdir /hy-tmp`  （使用该名称是因为最开始调试该项目时使用了恒源云GPU平台，因此后面便沿用了下来，您可修改为任意地址，但注意后面代码中出现的任何相关地址都需要被替换）

`cd /hy-tmp` 进入目录

下载parallel_studio_xe_2019_update5_cluster_edition

`wget [http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/15809/parallel_studio_xe_2019_update5_cluster_edition.tgz](http://registrationcenter-download.intel.com/akdlm/irc_nas/tec/15809/parallel_studio_xe_2019_update5_cluster_edition.tgz)`

解压文件

`tar -zxvf parallel_studio_xe_2019_update5_cluster_edition.tgz`

把解压后得到的parallel_studio_xe_2019_update5_cluster_edition文件夹重命名为`ps`方便后续操作

`sudo mv parallel_studio_xe_2019_update5_cluster_edition/ ps/`

安装必要的库

`sudo apt update`

`apt-get install cpio`

`sudo apt-get install xorg`

`apt-get install libasound2-dev`

`sudo apt-get install libgtk2.0-dev`

`sudo apt-get install -y unzip`

`sudo apt-get install zip`

安装parallel_studio_xe_2019

`cd ps && ./install.sh`