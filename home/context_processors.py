from django.db.models import Count
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from document.models import MovementOfDocument, Document, Statement
from notification.models import Notification
from employee.models import User, Profile



def getting_info(request):
    
    try:
        profile = Profile.objects.select_related('account', 'position').get(account=request.user)
        if profile.account.is_director:
            stat_count = Statement.objects.filter(director=profile, is_open_view_director=False).count()
        elif profile.account.is_statement:
            stat_count = Statement.objects.filter(responsible=profile, is_open_view_responsible=False).count()
        else:
            stat_count = 0
        inbox_count = MovementOfDocument.objects.filter(responsible=profile, open_view=False).count()
        notification_count = Notification.objects.filter(user=profile, open_view=False).count()
        res = inbox_count + stat_count
    except AttributeError:
        inbox_count = 0
        notification_count = 0
    except TypeError:
        inbox_count = 0
        notification_count = 0
    except ObjectDoesNotExist:
        profile = None

    date_now = timezone.now()

    return locals()



