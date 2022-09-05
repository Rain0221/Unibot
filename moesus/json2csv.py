import os
import json
import csv
import codecs
import argparse


def parse(file):
    print(file)
    try:
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            return
        keys = []
        for line in data:
            for key in line.keys():
                if key not in keys:
                    keys.append(key)
        with open(file.replace('.json', '.csv'), 'wb') as f:
            f.write(codecs.BOM_UTF8)
        with open(file.replace('.json', '.csv'), 'a', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(keys)
            for item in data:
                values = [item[key] if key in item else None for key in keys]
                writer.writerow(values)
    except Exception as e:
        print(e, "file =", file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="*")
    parser.add_argument("-r", action='store_true')
    args = parser.parse_args()
    for dir in args.dir:
        if args.r:
            for root, _, files in os.walk(dir):
                for file in files:
                    if file.endswith(".json"):
                        file_name = os.path.join(root, file)
                        parse(file_name)
        else:
            if dir.endswith(".json"):
                parse(dir)


if __name__ == "__main__":
    main()
