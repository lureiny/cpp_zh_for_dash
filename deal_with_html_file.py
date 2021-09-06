from lxml import etree
import re
from bs4 import BeautifulSoup as bs
from bs4 import Comment
import pathlib
import multiprocessing
from multiprocessing import Pool
import os
import shutil
import sys
import time

labels_attrs = {
    # label_name: {attr: [attr_value, ...], ...}
    "div": {
        "id": ["cpp-head-second-base", "cpp-head-search", "cpp-head-personal", "cpp-toolbox", "cpp-navigation", "carbonads"],
        "class": ["t-example-live-link", ]
    },
    "ul": {
        "id": ["footer-info", "footer-places", "footer-icons"]
    },
    "meta": {
        "name": ["generator", "ResourceLoaderDynamicStyles"]
    },
    "link": {
        "rel": ["alternate", "edit", "shortcut icon", "search", "EditURI"]
    },
    "script": {
        "id": ["_carbonads_js", ""]
    }
}


def read(file):
    with open(file, "r", encoding="utf8") as opened_file:
        return opened_file.read()


def del_label_and_comments(data):
    root = bs(data, "lxml")

    # 删除注释
    for element in root(text=lambda text: isinstance(text, Comment)):
        element.extract()

    # 删除特定script标签
    for script in root.select("head > script[src]"):
        script.decompose()

    for label in labels_attrs.keys():
        for attr in labels_attrs[label].keys():
            for attr_value in labels_attrs[label][attr]:
                parse_str = "{label}[{attr}=\"{attr_value}\"]".format(label=label,
                                                                      attr=attr, attr_value=attr_value)
                for el in root.select(parse_str):
                    el.decompose()

    return str(root)


def write(file, root):
    with open(file, "w") as opened_file:
        opened_file.write(root)


def traverse_dir(path: pathlib.Path, files: list):
    if not path.exists:
        print("not exist: ", path)
    elif path.is_file() and path.suffix == ".html":
        files.append(path)
    elif path.is_dir():
        # 遍历目录
        for child in path.iterdir():
            traverse_dir(child, files)


def deal_with_file(files, index):
    sys.stdout.write("\rdeal with: " + str(files[index]) + "\n进度: {:.2f}%({}/{})".format((index + 1) / len(files) * 100, index + 1, len(files)))

    data = read(files[index])
    root = del_label_and_comments(data)
    write(files[index], root)

# 删除无用文件和无用目录，缩减文档体积
def remove_unuseful_file(paths: pathlib.Path):
    for path in paths.iterdir():
        if re.search(r"^[A-Z]\S+:[\w!@#$%^&*/()<>=+-]+", path.name):
            if path.is_file():
                os.remove(path)
            elif path.is_dir():
                shutil.rmtree(path)


if __name__ == "__main__":
    doc_path = pathlib.Path("cpp_zh.docset/Contents/Resources/Documents/")
    files = list()

    # 先处理无用文件(夹)
    remove_unuseful_file(doc_path / "zh.cppreference.com/w")

    traverse_dir(doc_path / "zh.cppreference.com/w", files)

    # 创建线程池
    WORKER =  multiprocessing.cpu_count() + 1
    pool = Pool(processes=WORKER)

    for index in range(len(files)):
        # 判断当前进程数量
        while len(pool._cache) >= WORKER:
            pass

        pool.apply_async(deal_with_file, (files, index))

    # 等待全部进程结束
    while len(pool._cache) > 0:
        pass
    
    sys.stdout.write("\n")
