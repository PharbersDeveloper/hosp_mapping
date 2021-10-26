# 环境的安装

##. 安装python
我用的python 3.8

并将自己的python3指定目录（这一步都后面的东西很重要）

##. 安装程序

```python3
pip install PyQt5
pip install pyqt5-tools
```

重要的点来了，找到自己的qt_application 路径

```
python3 -m pip show qt5-applications
```
记住路径

##. 打开IDEA （Pycharm）


1. Designer
Preferences -> Tools -> External tools

- Program: /usr/local/lib/python3.8/site-packages/qt5_applications/Qt/bin/Designer.app
- Arguments: 
- Working Directory: $FileDir$

2. PyUIC
Preferences -> Tools -> External Tools

- Program: /usr/local/bin/python3
- Arguments: -m PyQt5.uic.pyuic $FileName$ -o $FileNameWithoutExtension$.py
- Working Directory: $FileDir$

## 开发流程如下

1. Desinger .ui 文件
2. .ui 文件 编译成 .py 文件
3. 开发

