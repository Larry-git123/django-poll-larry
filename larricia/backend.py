from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

class EmailBackend(object):

    # 重写认证方法
    # 这里接收email和password
    def authenticate(self, request, email=None, password=None):
        # 根据email查找用户
        try:
            user = User.objects.get(email=email)
        except DoesNotExist:
            # 用户不存在
            return None
        else:
            # 用户存在，检查密码
            if check_password(password, user.password):
                return user
            else:
                return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None