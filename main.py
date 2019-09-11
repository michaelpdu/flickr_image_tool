import os
import json
import argparse
from datetime import date
from icrawler import ImageDownloader
from icrawler.builtin import FlickrImageCrawler
from face_detector import find_face

root_dir = 'flickr_image_dir'

class FaceImageDownloader(ImageDownloader):
    """Downloader specified for face images.
    """
    def process_meta(self, task):
        # print(task)
        if task['filename'] is None:
            return
        image_path = os.path.join(root_dir, task['filename'])
        # task.img_size
        face_list = find_face(image_path)
        if len(face_list) == 0:
            os.remove(image_path)

# https://www.flickr.com/services/apps/create/noncommercial/?
# key：6ea696a89e485ce8b39cd052cc1dbd01
# c3acc5f2a23734b4

flickr_crawler = FlickrImageCrawler(apikey='6ea696a89e485ce8b39cd052cc1dbd01',
                                    feeder_threads=1,
                                    parser_threads=4,
                                    downloader_threads=16,
                                    downloader_cls=FaceImageDownloader,
                                    storage={'root_dir': root_dir})
flickr_crawler.crawl(max_num=576172, tags='chinese,girl', \
                     size_preference=['large', 'large 1600', 'large 2048'], \
                     min_upload_date=date(2010, 5, 25))

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Command Usages')
#     parser.add_argument("-c", action="store", dest='command', type=str, \
#                         help="Options: (3_target_avg|specific_target)")
#     args = parser.parse_args()