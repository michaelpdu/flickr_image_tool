import os
import json
import math
import argparse
from datetime import date
from icrawler import ImageDownloader
from icrawler.builtin import FlickrImageCrawler
from face_detector import find_face

ROOT_DIR = 'flickr_image_dir'
SUB_DIR = ''

class FaceImageDownloader(ImageDownloader):
    """Downloader specified for face images.
    """
    def process_meta(self, task):
        # print(task)
        if task['filename'] is None:
            return
        image_path = os.path.join(SUB_DIR, task['filename'])
        # task.img_size
        face_list = find_face(image_path)
        if len(face_list) == 0:
            os.remove(image_path)

def crawl_images(tags, index, batch_size):
    # https://www.flickr.com/services/apps/create/noncommercial/?
    # key：6ea696a89e485ce8b39cd052cc1dbd01
    # c3acc5f2a23734b4
    global SUB_DIR

    i = 5*index+1
    subdir_name = tags.replace(',', '_')
    SUB_DIR = os.path.join(ROOT_DIR, '{}_{}'.format(subdir_name, i))

    flickr_crawler = FlickrImageCrawler(apikey='6ea696a89e485ce8b39cd052cc1dbd01',
                                        feeder_threads=1,
                                        parser_threads=1,
                                        downloader_threads=8,
                                        downloader_cls=FaceImageDownloader,
                                        storage={'root_dir': SUB_DIR})
    flickr_crawler.crawl(max_num=batch_size, tags=tags, page=i, \
                        size_preference=['large', 'large 1600', 'large 2048'], \
                        min_upload_date=date(2010, 5, 25))

def main(args):
    epoch = int(math.ceil(args.count/args.batch_size))
    print('[MD] epoch=', epoch)
    for i in range(0, epoch):
        print('[MD] index=', i)
        crawl_images(args.tags, i, args.batch_size)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command Usages')
    parser.add_argument("-t", "--tags", type=str, default='chinese,girl', help="")
    parser.add_argument("-c", "--count", type=int, default=100, help="count of download images")
    parser.add_argument("-b", "--batch_size", type=int, default=500, help="batch size")
    args = parser.parse_args()
    main(args)
