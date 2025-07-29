from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
class Command(BaseCommand):
    help = 'Tự động xoá tất cả dữ liệu và khởi tạo lại cơ sở dữ liệu'
    def handle(self, *args, **options):
        if os.path.exists('db.sqlite3'):
            os.remove('db.sqlite3')
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS('Đã reset database & dữ liệu về trạng thái mặc định!'))
