from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
class Command(BaseCommand):
    help = 'Tự động xoá tất cả dữ liệu và khởi tạo lại cơ sở dữ liệu'
    def handle(self, *args, **options):
        if os.path.exists('db.sqlite3'):
            os.remove('db.sqlite3')
        #remove all images in media/images
        media_images_path = os.path.join('media', 'images')
        if os.path.exists(media_images_path):
            for filename in os.listdir(media_images_path):
                file_path = os.path.join(media_images_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        call_command('migrate')
        call_command('makemigrations')
        self.stdout.write(self.style.SUCCESS('Đã reset database & dữ liệu về trạng thái mặc định!'))
