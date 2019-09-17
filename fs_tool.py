import os
import argparse
import hashlib

def get_digest(file_path):
    h = hashlib.sha1()
    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def rename_images(input_dir, output_dir):
    if os.path.exists(input_dir):
        os.makedirs(output_dir)
    for root, _, files in os.walk(input_dir):
        for name in files:
            img_path = os.path.join(root, name)
            par_dir = os.path.split(root)[1]
            new_img_path = os.path.join(output_dir, par_dir+'_'+name)
            print(new_img_path)
            os.rename(img_path, new_img_path)

def remove_duplicates(input_dir):
    sha1list = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            img_path = os.path.join(root, name)
            sha1 = get_digest(img_path)
            if not sha1 in sha1list:
                sha1list.append(sha1)
            else:
                print('Remove duplicated image,', img_path)
                os.remove(img_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command Usages')
    parser.add_argument("-i", "--input", type=str, help="input")
    parser.add_argument("-o", "--output", type=str, help="output")
    parser.add_argument("-r", "--rename", action="store_true", help="rename image files by parent dir name")
    parser.add_argument("-d", "--duplicate", action="store_true", help="remove duplicated files")
    args = parser.parse_args()

    if args.input:
        if args.rename:
            rename_images(args.input, args.output)
        elif args.duplicate:
            remove_duplicates(args.input)
        else:
            pass
    else:
        parser.print_help()