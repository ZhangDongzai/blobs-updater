# Blobs Updater
Blobs Updater is a tool for aosp to delete and copy blobs from a vendor tree to another one.

## Usage
set path in ./main.py
```python3
SOURCE_PATH = "the-path-where-copy-from/proprietary"
TARGET_PATH = "the-path-where-copy-to/proprietary"
```

cd to device tree and make changes to proprietary-files.txt without a commit
```shell
git diff proprietary-files.txt > (the-project-path)/git-diff.txt
```

cd to the project dir
```shell
./format.py ./git-diff.txt > ./update.txt
./main.py ./update.txt
./clean.sh
```
