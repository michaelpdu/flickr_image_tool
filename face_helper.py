#coding=utf-8
import face_recognition
from PIL import Image, ImageDraw
import numpy as np
import os
import argparse
import multiprocessing
import logging

SUPPORTED_IMAGE_EXT = ['.jpg', '.png']

def is_image_file(filename):
    _, ext = os.path.splitext(filename)
    if not ext.lower() in SUPPORTED_IMAGE_EXT:
        return False
    else:
        return True

def find_faces(im, threshold=120):
    ret_list = []
    image = np.array(im.convert('RGB'))
    # (top, right, bottom, left)
    face_locations = face_recognition.face_locations(image)
    logging.debug('face locations: {}'.format(face_locations))
    for (top, right, bottom, left) in face_locations:
        width = right-left
        height = bottom-top
        logging.debug('width: {}, height: {}'.format(width, height))
        # minimum size
        if width < threshold or height < threshold:
            continue
        ret_list.append((top, right, bottom, left))
    return ret_list

def adjust_cropped_locations(width, height, locations):
    cropped_locations = []
    for (top, right, bottom, left) in locations:
        #
        face_height = bottom - top
        face_width = right - left
        logging.debug('face_height: {}, face_width: {}'.format(face_height, face_width))
        #
        new_top = top - face_height
        top = new_top if new_top > 0 else 0

        new_bottom = bottom + face_height
        bottom = new_bottom if new_bottom < height else height

        new_left = left - face_width
        left = new_left if new_left > 0 else 0

        new_right = right + face_width
        right = new_right if new_right < width else width

        #
        face_height = bottom - top
        face_width = right - left
        logging.debug('[new] face_height: {}, face_width: {}'.format(face_height, face_width))

        # 
        # adjust image location
        if face_height > face_width:
            gap = face_height - face_width
            if top == 0:
                bottom = bottom-gap
            elif bottom == height:
                top = top+gap
            else:
                bottom = bottom-int(gap/2)
                top = top+int(gap/2)
        else:
            gap = face_width - face_height
            if left == 0:
                right = right-gap
            elif right == width:
                left = left+gap
            else:
                right = right-int(gap/2)
                left = left+int(gap/2)

        #
        face_height = bottom - top
        face_width = right - left
        logging.debug('[adjusted] face_height: {}, face_width: {}'.format(face_height, face_width))

        #
        cropped_locations.append((top, right, bottom, left))
    return cropped_locations

def draw_image_with_face_rectangle(image_path, locations):
    im = Image.open(image_path)
    width, height = im.size
    locations = adjust_cropped_locations(width, height, locations)
    draw = ImageDraw.Draw(im)
    for (top, right, bottom, left) in locations:
        #
        draw.line((right, top, right, bottom), fill=128, width=10)
        draw.line((left, top, right, top), fill=128, width=10)
        draw.line((left, top, left, bottom), fill=128, width=10)
        draw.line((left, bottom, right, bottom), fill=128, width=10)
    im.show()

# 从图像中截取1024x1024的区域，包含人脸的图像
def crop_square_by_face(image_path, output_dir, size=1024):
    #
    dir_path, filename = os.path.split(image_path)
    filename_wo_ext, ext = os.path.splitext(filename)
    _, dir_name = os.path.split(dir_path)
    output_subdir = os.path.join(output_dir, dir_name)
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    #
    im = Image.open(image_path)
    width, height = im.size
    logging.debug('width: {}, height: {}'.format(width, height))

    face_locations = find_faces(im)
    if len(face_locations) > 1:
        logging.info('more than 1 face locations in the image, {}'.format(image_path))
        return

    cropped_locations = adjust_cropped_locations(width, height, face_locations)

    index = 1
    for (top, right, bottom, left) in cropped_locations:
        cropped_width = right-left
        cropped_height = bottom-top
        if cropped_width < size or cropped_height < size:
            logging.info('cropped image size < {}, {}'.format(size, image_path))
            continue
        
        cropped_path = os.path.join(output_dir, dir_name, '{}_{}{}'.format(filename_wo_ext, index, ext))
        im.crop((left, top, right, bottom)).resize((size,size)).save(cropped_path)

        index += 1

def process_image_list(cpu_index, image_list, output_dir):
    index = 0
    last_image = ''
    for image_path in image_list:
        try:
            index += 1
            last_image = image_path
            crop_square_by_face(image_path, output_dir)
        except Exception as _:
            logging.warn("exception in CPU {} when process: {}".format(cpu_index, image_path))
    logging.info("process_image_list done! CPU: {}, image_list length: {}, index: {}, last_image: {}".format(cpu_index, len(image_list), index, last_image))

def batch_crop_images(image_path, output_dir):
    image_path_list = []
    for root, _, files in os.walk(image_path):
        for name in files:
            image_path_list.append(os.path.join(root, name))
    process_image_list(image_path_list, output_dir)

def crop_images(image_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if os.path.isfile(image_path):
        crop_square_by_face(image_path, output_dir)
    elif os.path.isdir(image_path):
        batch_crop_images(image_path, output_dir)
    else:
        pass

def start_multi_processes(image_path, list_file_path, output_dir, cpu_count):
    #
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    #
    accomplished_file_list = []
    if list_file_path and os.path.exists(list_file_path) and os.path.isfile(list_file_path):
        with open(list_file_path, 'r') as fh:
            for line in fh.readlines():
                accomplished_file_list.append(line.strip())
    #
    image_list_group = []
    for _ in range(0, cpu_count):
        image_list_group.append([])
    index = 0
    count_in_accomplished_list = 0
    for root, _, files in os.walk(image_path):
        for name in files:
            if not is_image_file(name):
                continue
            image_file_path = os.path.join(root, name)
            if image_file_path in accomplished_file_list:
                logging.debug('find in accomplished_file_list, {}'.format(image_file_path))
                count_in_accomplished_list += 1
                continue
            image_list_group[index%cpu_count].append(image_file_path)
            index += 1
    logging.info('find {} in accomplished file list'.format(count_in_accomplished_list))
    jobs = []
    for i in range(0, cpu_count):
        logging.info('index: {}, length: {}'.format(i, len(image_list_group[i])))
        p = multiprocessing.Process(target=process_image_list, args=(i,image_list_group[i],output_dir,))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
    print('[MD] Completed!')

def crop_images_multi_process(image_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if os.path.isfile(image_path):
        crop_square_by_face(image_path, output_dir)
    elif os.path.isdir(image_path):
        batch_crop_images(image_path, output_dir)
    else:
        pass
# 
def print_multi_faces_image(image_path):
    im = Image.open(image_path)
    count = len(find_faces(im, 1))
    if count > 1:
        logging.info('more than 1 faces in {}'.format(image_path))

def check_face_count_in_image(image_dir):
    for root, _, files in os.walk(image_dir):
        for name in files:
            if not is_image_file(name):
                continue
            image_path = os.path.join(root, name)
            logging.debug('process {}'.format(image_path))
            print_multi_faces_image(image_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command Usages')
    parser.add_argument("-i", "--input", type=str, help="input")
    parser.add_argument("-o", "--output", type=str, default="output_dir", help="output")
    parser.add_argument("-d", "--draw", action="store_true", help="draw face rectangle in image")
    parser.add_argument("-c", "--crop", action="store_true", help="crop face areas")
    parser.add_argument("-p", "--cpu_count", type=int, default=0, \
        help="cpu count for multiprocessing, default value is 0, which means all of cpu would be used")
    parser.add_argument("-m", "--multi", action="store_true", help="print multiple faces in image")
    parser.add_argument("-l", "--list_file", type=str, help="list file contains accomplished files")
    args = parser.parse_args()

    global_cpu_count = multiprocessing.cpu_count()
    logging.basicConfig(filename='face_helper.log', level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if args.input and os.path.exists(args.input):
        if args.draw:
            im = Image.open(args.input)
            locations = find_faces(im)
            draw_image_with_face_rectangle(args.input, locations)
        elif args.crop:
            if args.cpu_count >= 0:
                if args.cpu_count == 0:
                    cpu_count = global_cpu_count
                elif args.cpu_count <= global_cpu_count:
                    cpu_count = args.cpu_count
                else:
                    cpu_count = global_cpu_count
                logging.info('start multiprocessing to crop images, process count = {}'.format(cpu_count))
                start_multi_processes(args.input, args.list_file, args.output, cpu_count)
            else:
                logging.info('crop images in single process.')
                # crop_images(args.input, args.output)
        elif args.multi:
            check_face_count_in_image(args.input)
        else:
            pass
    else:
        parser.print_help()