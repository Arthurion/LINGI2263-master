#! /usr/local/bin/python3

import codecs
import sys
import yaml

from os.path import basename


def check_file(file):

    # Read yaml file
    try:
        with codecs.open(file, mode='r', encoding='utf8', errors="strict") as f:
            ingredients = yaml.load(f)
    except UnicodeDecodeError:
        msg = "Error due to encoding."
        return (False, msg) 

    ok = isinstance(ingredients, list) 
    if not ok:
        msg = "The results file does not describe a list."
        return (False, msg) 

    results  = [check_ingredient(ingredient) for ingredient in ingredients]
    messages = "\n".join(msg for _,msg in results if msg)
    status   = all(status for status,_ in results)

    return (status, messages)


GOOD_KEYS = ["quantity", "unit", "ingredient"]

def check_ingredient(ingredient):


    if not isinstance(ingredient, dict):
        msg  = "Error: an ingredient is not represented as a dictionary\n"
        msg += "-----> " + str(ingredient)
        return (False, msg)

    keys = list(ingredient.keys())
    if len(keys) == 0:
        msg  = "Error: empty ingredient"
        return (False, msg)

    bad_keys = []
    for k in keys:
        if k not in GOOD_KEYS:
            bad_keys.append(k)

    if len(bad_keys):
        msg  = "Error: bad keys in the ingredient description\n"
        msg += "-----> " + " / ".join(bad_keys)
        return (False, msg)

    return (True,"")
    
def print_filename(filename):
    bname = basename(filename)
    bname = "File: " + bname
    length = len(bname)

    total_len = 80
    delta = total_len - length - 1

    return bname + " " + "=" * delta


if __name__ == '__main__':

    input_files = sys.argv[1:]
    input_files = [f for f in input_files if f.endswith("yaml")]

    global_status = True
    for input_file in input_files:

        ok, msg = check_file(input_file)
        if not ok:
            global_status = False
            print(print_filename(input_file))
            print(msg)

    if global_status:
        print("All files are correctly formatted.")
    
    