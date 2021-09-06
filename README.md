# cpp_zh for dash

基于dash官方提供的英文cpp文档索引, 使用`zh.cppreference.com`网站源文件构建dash可用的cpp_zh文档。

## 文件说明

1. `create_docset.py`: 根据html生成cpp_zh.docset文档的方法
2. `deal_with_html_file.py`: 处理cpp_zh.docset中无用的源文件及源代码, 缩减生成的文档体积
3. `icon.png`: 生成文档的icon
4. `requestments.txt`: python3环境的依赖列表
5. `optimizedIndex.dsidx`: dash官方提供的英文cpp文档数据库索引文件

## 使用方法

1. 镜像下载zh.cppreference.com网站源文件
```shell
    wget  -e robots=off -r -p -np -k -E .html https://zh.cppreference.com/w/
```
2. 配置python环境
```shell
    pip3 install -r requestments.txt
```
3. 创建`cpp_zh.docset`
```python
    python3 create_docset.py
```
4. 清理`cpp_zh.docset`中无用源文件即源文件中无用源码
```python
    python3 deal_with_html_file.py
```