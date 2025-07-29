from lockers.models import Lock, User, Log, UserImage, AdminLock, Image
from django.http import JsonResponse
from . import define
def write_log(code, details = "", locker = None, user_id = None):
    try:
        if (code == 0):
            pass
        elif(code == 1):
            if not locker:
                return JsonResponse({'error': 'Locker ID is required for code 1'}, status=400)
            details = define.msg[1] % (locker.lock_id, locker.board_id)
        elif(code == 2):
            if not locker:
                return JsonResponse({'error': 'Locker ID is required for code 2'}, status=400)
            if not locker.user:
                return JsonResponse({'error': 'Locker must be registered to a user for code 2'}, status=400)
            details = define.msg[2] % (locker.lock_id, locker.board_id, locker.user.id)
        elif(code == 3):
            if not locker:
                return JsonResponse({'error': 'Locker ID is required for code 3'}, status=400)
            details = define.msg[3] % (locker.lock_id, locker.board_id)
        elif(code == 4):
            if not locker:
                return JsonResponse({'error': 'Locker ID is required for code 4'}, status=400)
            details = define.msg[4]
        elif(code == 5):
            details = define.msg[5]
        elif(code == 6):
            details = define.msg[6]
        elif(code == 7):
            if not user_id:
                return JsonResponse({'error': 'User ID is required for code 7'}, status=400)
            details = define.msg[7] % user_id
        elif(code == 8):
            if not user_id:
                return JsonResponse({'error': 'User ID is required for code 8'}, status=400)
            details = define.msg[8] % user_id
        elif(code == 9):
            if not user_id:
                return JsonResponse({'error': 'User ID is required for code 9'}, status=400)
            details = define.msg[9] % user_id
        elif(code == 10):
            if not user_id:
                return JsonResponse({'error': 'User ID is required for code 10'}, status=400)
            details = define.msg[10] % user_id
        else:
            return JsonResponse({'error': 'Invalid code'}, status=400)
        log = Log.objects.create(
            code = code,
            details = details,
            locker = locker,
            mark = False,
        )
        return JsonResponse({'success': True, 'log_id': log.id}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


