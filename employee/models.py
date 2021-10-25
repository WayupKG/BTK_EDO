from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.contrib.auth.hashers import make_password

from document.services import gen_slug


def upload_to_img(instance, filename):
    list_file = filename.split('.')
    return 'Profile/%s/%s/' % (instance.account.username, f'{gen_slug(instance.first_name, instance.last_name)}.{list_file[-1]}')


class UserManager(BaseUserManager):
    def create_user(self, last_name, first_name, username, email, password=None, **kwargs):
        """Создайте и верните "Пользователя` с электронной почтой, именем пользователя и паролем."""
        if last_name is None:
            raise TypeError("У пользователя должно быть Фамилия.")
        if first_name is None:
            raise TypeError("У пользователя должно быть Имя.")
        if username is None:
            raise TypeError("У пользователя должно быть Имя пользователя.")
        if email is None:
            raise TypeError("У пользователя должно быть Email.")
        user = self.model(last_name=last_name, first_name=first_name, username=username,
                              email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, last_name, first_name, username, email, password):
        """Создайте и верните " Пользователя` с правами суперпользователя (администратора)."""
        user = self.create_user(last_name, first_name, username, email, password)
        user.is_superuser = True
        user.is_active = True
        user.is_admin = True
        user.is_analytica = True
        user.is_staff = True
        user.save(using=self._db)
        return user



class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).order_by('-created')

class ProfileActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(account__is_active=True).order_by('-created')


class User(AbstractBaseUser, PermissionsMixin):
    last_name = models.CharField('Фамилия', max_length=20)
    first_name = models.CharField('Имя', max_length=20)
    sur_name = models.CharField('Отчество', max_length=20, null=True, blank=True)
    username = models.CharField('Имя пользователя', db_index=True, max_length=255)
    email = models.EmailField('Электронная почта', db_index=True, unique=True)

    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_analytica = models.BooleanField(default=False)
    is_statement = models.BooleanField(default=False)
    is_director = models.BooleanField(default=False, verbose_name='Директор', 
                                      help_text='Ставте голучку если этот пользователь является Директором оргенизации')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["last_name", "first_name", "username"]

    objects = UserManager()
    active = ActiveManager()


    def get_full_name(self):
        return f'{self.last_name} {self.first_name} {self.sur_name if self.sur_name else ""}'

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.sur_name if self.sur_name else ""}'

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Аккаунт сотрудника'
        verbose_name_plural = 'Аккаунты сотрудников'


class Profile(models.Model):
    PAUL = (
        ('Male', 'Мужской'),
        ('Female', 'Женский')
    )
    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    last_name = models.CharField('Фамилия', max_length=20)
    first_name = models.CharField('Имя', max_length=20)
    sur_name = models.CharField('Отчество', max_length=20, null=True, blank=True)
    position = models.ForeignKey('Position', verbose_name='Должность', on_delete=models.PROTECT,
                                 related_name='employees', null=True, blank=True)
    date_of_birth = models.DateField('День рождения', null=True, blank=True)
    paul = models.CharField('Пол', max_length=10, choices=PAUL)
    tel_number = models.CharField('Номер телефона', max_length=50, null=True, blank=True)
    avatar_image = models.ImageField('Фото', upload_to=upload_to_img, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active = ProfileActiveManager()

    def paul_verbose(self):
        return dict(Profile.PAUL)[(self.paul)]

    def get_full_name(self):
        return f'{self.last_name} {self.first_name} {self.sur_name if self.sur_name else ""}'

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


    class Meta:
        ordering = ('-created',)
        verbose_name = 'Анкета сотрудника'
        verbose_name_plural = 'Анкеты сотрудников'


class Position(models.Model):
    name = models.CharField('Полное название', max_length=255, unique=True)
    abbreviated_name = models.CharField('Сокращенное название', max_length=255)
    doc_name = models.CharField('Название для заявление или рапорта', max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class SettingsUser(models.Model):
    """Settings User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    is_mail_inbox = models.BooleanField('Включить уведомление о новом документе', default=False)
    is_mail_movement = models.BooleanField('Включить уведомление о действие документах (при ответе на ваш документ)',
                                           default=False)
    is_mail_ad = models.BooleanField('Включить уведомление о новых событиях (Новости & Мероприятия)', default=False)
    objects = models.Manager()

    def __str__(self):
        return f'{self.user.last_name} {self.user.first_name}'

    class Meta:
        verbose_name = 'Настройка'
        verbose_name_plural = 'Настройки'
