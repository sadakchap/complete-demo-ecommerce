from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError(_('Users Must have an Email Address'))
        if not password:
            raise ValueError(_('Users must have a password'))
        
        user_obj = self.model(
            email=self.normalize_email(email)
        )
        user_obj.set_password(password)
        user_obj.active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.save(using=self._db)
        return user_obj
    
    def create_staffuser(self, email, password=None):
        return self.create_user(email, password, is_staff=True)
    
    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password,
            is_staff=True,
            is_admin=True
        )
        return user


class User(AbstractBaseUser):
    email       = models.EmailField(_('email address'), unique=True)
    first_name  = models.CharField(_("First name"), max_length=255, blank=True, null=True)
    last_name   = models.CharField(_("Last name"), max_length=255, blank=True, null=True)
    active      = models.BooleanField(_("active"), default=True)
    staff       = models.BooleanField(_("staff"), default=False)
    admin       = models.BooleanField(_("admin"), default=False)

    #passowrd and last_login are included from AbstractBaseUser class

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def get_full_name(self):
        return self.first_name + self.last_name
    
    def get_short_name(self):
        if self.first_name:
            return self.first_name
        return None
    
    def email_user(self, subject, message, **kwargs):
        send_mail(subject, message, settings.EMAIL_HOST_USER,
                  [self.email], **kwargs)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_superuser(self):
        return self.admin

    @property
    def is_staff(self):
        return self.admin
    
    @property
    def is_active(self):
        return self.active

class Profile(models.Model):
    GENDER_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other'),
    )
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic     = models.ImageField(_(''), upload_to='user_profile_pic/', blank=True, null=True)
    phone_no        = models.CharField(max_length=17, blank=True, null=True, unique=True)
    gender          = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    confirmed_email = models.BooleanField(default=False)
    confirmed_date  = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.get_short_name()

    def set_confirmed_date(self):
        self.confirmed_date = timezone.now()
        self.save()
