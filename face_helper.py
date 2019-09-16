import face_recognition
from PIL import Image
import os
import argparse

def find_face(image_path):
    ret_list = []
    image = face_recognition.load_image_file(image_path)
    # (top, right, bottom, left)
    face_locations = face_recognition.face_locations(image)
    # print(face_locations)
    for (top, right, bottom, left) in face_locations:
        width = right-left
        height = bottom-top
        # print('width: ', width, ', height: ', height)
        # minimum size
        if width < 120 or height < 120:
            continue
        ret_list.append((top, right, bottom, left))
    return ret_list

#
# 从图像中截取640*640，包含人脸的图像
#
def crop_square_by_face(image_path, output_dir):
    #
    _, filename = os.path.split(image_path)
    filename_wo_ext, ext = os.path.splitext(filename)
    #
    im = Image.open(image_path)
    width, height = im.size
    print('[MD] width:', width, ', height:', height)

    face_locations = find_face(image_path)
    index = 1
    for (top, right, bottom, left) in face_locations:
        face_width = right-left
        face_height = bottom-top

        print('[MD] top:', top, ', right:', right, ', bottom:', bottom, ', left:', left)
        print('[MD] face_width:', face_width, ', face_height:', face_height)
        # 3*face_height<640 or 3*face_width<640

        cropped_path = os.path.join(output_dir, '{}_{}{}'.format(filename_wo_ext, index, ext))

        if 3*face_height < 640 or 3*face_width<640:
            print('[MD] {}, small than 640'.format(image_path))
        else:
            if top>face_height and bottom+face_height<height \
                and left>face_width and right+face_width<width:
                print('[MD] Save cropped image:', cropped_path)
                # left, top, right, bottom
                im.crop((left-face_width, top-face_height, right+face_width,    \
                    bottom+face_height)).resize((640,640)).save(cropped_path)
            elif height > 3*face_height*0.9 and width > 4*face_width*0.9 \
                and left>face_width and width-right>face_width:
                print('[MD] larger than 0.9')
                if top>0.6*face_height and (height-bottom)>1.2*face_height:
                    print('[MD] Save cropped image:', cropped_path)
                    # left, top, right, bottom
                    im.crop((left-face_width, 0, right+face_width,    \
                    3*face_height)).resize((640,640)).save(cropped_path)
                else:
                    print('[MD] yyy')
            else:
                print('[MD] {}, not in the middle area of cropped image'.format(image_path))
        index += 1

def batch_crop_images(image_path, output_dir):
    for root, _, files in os.walk(image_path):
        for name in files:
            crop_square_by_face(os.path.join(root, name), output_dir)

def crop_image(image_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if os.path.isfile(image_path):
        crop_square_by_face(image_path, output_dir)
    elif os.path.isdir(image_path):
        batch_crop_images(image_path, output_dir)
    else:
        pass

#
# 
def remove_multi_faces_image(image_path):
    if len(find_face(image_path)) > 1:
        print('[MD] Multi faces in image, ', image_path)

def face_pose(image_path):
    pass

def black_white_images(image_path):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command Usages')
    parser.add_argument("-i", "--input", type=str, help="input")
    parser.add_argument("-o", "--output", type=str, default="output_dir", help="output")
    parser.add_argument("-l", "--locations", action="store_true", help="print face locations")
    parser.add_argument("-c", "--crop", action="store_true", help="crop ")
    args = parser.parse_args()

    if args.input:
        if args.locations:
            locations = find_face(args.input)
            print(locations)
        elif args.crop:
            crop_image(args.input, args.output)
    else:
        parser.print_help()