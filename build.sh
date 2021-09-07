#!/usr/bin/sh

DATE=`date +%Y%m%d`
CPP_TAR=zh.cppreference.com-${DATE}.tgz

FOLDER=zh.cppreference.com

if [ ! -d "${FOLDER}" ]; then
    wget  -e robots=off -r -p -np -k -E .html https://zh.cppreference.com/w/
fi

pip install -r requestments.txt

python3 create_docset.py

python3 deal_with_html_file.py

cp icon.png cpp_zh.docset/

tar czf cpp_zh.tgz cpp_zh.docset

tar czf ${CPP_TAR} zh.cppreference.com

echo ${1} | gh auth login --with-token

gh release create ${DATE} --notes  "" optimizedIndex.dsidx