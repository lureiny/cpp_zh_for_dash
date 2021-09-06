import sqlite3
import re
import pathlib
import os
import shutil
from multiprocessing import Pool
import multiprocessing


def write_db_file(cmd, db_file):
    con = sqlite3.connect(str(db_file / "docSet.dsidx"))
    cur = con.cursor()
    try:
        cur.execute(cmd)
        con.commit()
    except Exception as e:
        print(e)
        con.rollback()

    con.close()


def read_db_file():
    con = sqlite3.connect('optimizedIndex.dsidx')
    cur = con.cursor()
    base_path = root

    results = list()

    try:
        for row in cur.execute('select * from searchIndex;'):
            name = row[1]
            type = row[2]
            path = re.search("(en.cppreference.com/w/.+)", row[3]).group()

            path = re.sub("^en\.", "zh.", path)

            if (base_path / path).exists():
                results.append((name, type, path))

    except Exception as e:
        print(e)
        con.rollback()

    con.close()
    return results


def create_docset_dir(dir: pathlib.Path):
    if not dir.exists():
        dir.mkdir(parents=True)

# 复制文件到docset目录下


def copy_html(src: pathlib.Path, dst: pathlib.Path):
    shutil.copytree(src, dst, dirs_exist_ok=True)


def create_info_plist(path: pathlib.Path):
    info_plist_path = (path / "Info.plist")

    with open(info_plist_path, "w", encoding="utf8") as opened_file:
        opened_file.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>{doc_name}</string>
	<key>CFBundleName</key>
	<string>{doc_name}</string>
	<key>DocSetPlatformFamily</key>
	<string>{doc_name}</string>
	<key>isDashDocset</key>
	<true/>
	<key>dashIndexFilePath</key>
	<string>zh.cppreference.com/w/首页.html</string>
</dict>
</plist>""".format(doc_name=doc_name))


def multi_process_write_db_file(cmd, percent, db_file):
    print("\r进度: {:.2f}%".format(percent), end="")
    write_db_file(cmd, db_file)


if __name__ == "__main__":
    doc_name = "cpp_zh"
    html_path = pathlib.Path("zh.cppreference.com")
    doc_path = pathlib.Path(
        "{doc_name}.docset/Contents/Resources/Documents".format(doc_name=doc_name))
    root = pathlib.Path("./")

    create_docset_dir(doc_path)
    copy_html(html_path, doc_path / html_path)
    create_info_plist(doc_path.parent.parent)

    # 创建表
    write_db_file(
        "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);", doc_path.parent)
    write_db_file(
        "CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);", doc_path.parent)

    results = read_db_file()

    # 创建线程池
    WORKER = multiprocessing.cpu_count() + 1
    pool = Pool(processes=WORKER)

    for index in range(len(results)):
        # 判断当前进程数量
        while len(pool._cache) >= WORKER:
            pass

        cmd = "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('{}', '{}', '{}');".format(
            results[index][0], results[index][1], results[index][2])

        pool.apply(multi_process_write_db_file,
                   (cmd, ((index + 1) / len(results) * 100), doc_path.parent))

    # 等待全部进程结束
    while len(pool._cache) > 0:
        pass
