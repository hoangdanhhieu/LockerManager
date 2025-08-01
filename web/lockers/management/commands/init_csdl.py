from django.core.management.base import BaseCommand
from lockers.models import Lock, AdminLock
from django.contrib.auth.hashers import make_password, is_password_usable

class Command(BaseCommand):
    help = 'Khởi tạo dữ liệu mẫu cho CSDL'
    def handle(self, *args, **options):
        self.stdout.write('Hello, World!')
        # Create locks for boards 1-32, each with lock_ids 1-16
        locks_to_create = []
        for board_id in range(1, 33):  # 1 to 32
            for lock_id in range(1, 17):  # 1 to 16
                locks_to_create.append(Lock(board_id=board_id, lock_id=lock_id))
        # Bulk create Admin_password
        admin_password = AdminLock(password=make_password('Hoanghieu.2702'))
        admin_password.save()
        Lock.objects.bulk_create(locks_to_create)
        self.stdout.write(self.style.SUCCESS('Đã hoàn thành thêm dữ liệu!'))

