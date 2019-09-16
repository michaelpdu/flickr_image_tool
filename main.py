import os
import json
import math
import argparse
from datetime import date
from icrawler import ImageDownloader
from icrawler.builtin import FlickrImageCrawler
from face_helper import find_face

ROOT_DIR = 'flickr_image_dir'
SUB_DIR = ''

def set_sub_dir(sub_dir):
    global SUB_DIR
    SUB_DIR = sub_dir
    print('[MD] Set SUB_DIR:', SUB_DIR)

def get_sub_dir():
    # print('[MD] Get SUB_DIR:', SUB_DIR)
    return SUB_DIR

class FaceImageDownloader(ImageDownloader):
    """Downloader specified for face images.
    """
    def process_meta(self, task):
        # print(task)
        if task['filename'] is None:
            return
        subdir = get_sub_dir()
        image_path = os.path.join(subdir, task['filename'])
        # task.img_size
        face_list = find_face(image_path)
        if len(face_list) == 0:
            os.remove(image_path)

def crawl_images(tags, index, batch_size):
    # https://www.flickr.com/services/apps/create/noncommercial/?
    # key：6ea696a89e485ce8b39cd052cc1dbd01
    # c3acc5f2a23734b4

    i = int(batch_size/100)*index+1
    print('index:',index,', i:',i)
    subdir_name = tags.replace(',', '_')
    subdir = os.path.join(ROOT_DIR, '{}_{}'.format(subdir_name, index))
    print(subdir)
    set_sub_dir(subdir)

    flickr_crawler = FlickrImageCrawler(apikey='6ea696a89e485ce8b39cd052cc1dbd01',
                                        feeder_threads=1,
                                        parser_threads=1,
                                        downloader_threads=8,
                                        downloader_cls=FaceImageDownloader,
                                        storage={'root_dir': subdir})
    flickr_crawler.crawl(max_num=batch_size, tags=tags, page=i, \
                        size_preference=['large 2048', 'large 1600', 'large'], \
                        min_upload_date=date(2010, 5, 25))

def main(args):
    if args.batch_size % 100 != 0:
        print('[MD] batch size must be divided with 100.')
        return
    epoch = int(math.ceil(args.count/args.batch_size))
    print('[MD] epoch=', epoch)
    for i in range(0, epoch):
        print('[MD] index=', i)
        crawl_images(args.tags, i, args.batch_size)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command Usages')
    parser.add_argument("-t", "--tags", type=str, help="tags used in flickr search, such as, 'chinese,girl'")
    parser.add_argument("-c", "--count", type=int, default=1500, help="count of download images, default is 1500")
    parser.add_argument("-b", "--batch_size", type=int, default=500, help="batch size, default is 500")
    args = parser.parse_args()

    if args.tags:
        main(args)
    else:
        parser.print_help()
