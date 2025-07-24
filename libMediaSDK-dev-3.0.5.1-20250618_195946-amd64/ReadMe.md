1、安装SDK包

```bash
`sudo dpkg -i libMediaSDK-dev-3.0.0.1-20250313_193026-amd64.deb`
```

   <img src=".\pic\screenshot-20250314-162049" alt="screenshot-20250314-162049" style="zoom:80%;" />

2、安装以后，运行 stitcherSDKTest, 出现下面信息，说明libMediaSDK安装成功

   <img src=".\pic\screenshot-20250314-162049.png" alt="screenshot-20250314-162049.png" style="zoom:80%;" />

3、可以直接使用stitcherSDKTest进行调试，也可以通过当前目录example下的main.cc进行修改进行调试，demo

​	编译指令如下：

```bash
`g++ main.cc -std=c++11 -lMediaSDK -lpthread -o testSDKDemo`
```

4、卸载SDK包

```bash
`sudo dpkg -r libMediaSDK-dev`
```

5、Note:

​    cuda版本： 11.1

​    g++版本:     g++ (Ubuntu 9.4.0-1ubuntu1~20.04.2) 9.4.0
