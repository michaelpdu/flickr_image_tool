import face_recognition
import sys

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

if __name__ == '__main__':
    print(find_face(sys.argv[1]))