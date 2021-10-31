from django.utils import timezone

from document.models import MovementOfDocument, Document, Statement
from notification.models import Notification
from check_list.models import CheckList


def getting_info(request):
    try:
        user = request.user
        if user.is_director:
            stat_count = Statement.objects.filter(director=user.profile, is_open_view_director=False).count()
        elif user.is_statement:
            stat_count = Statement.objects.filter(responsible=user.profile, is_open_view_responsible=False).count()
        else:
            stat_count = 0
        check_count = CheckList.objects.filter(author=user.profile, open_view=False).count()
        inbox_count = MovementOfDocument.objects.filter(responsible=user.profile, open_view=False).count()
        notification_count = Notification.objects.filter(user=user.profile, open_view=False).count()
        res = inbox_count + stat_count
    except AttributeError:
        check_count = 0
        inbox_count = 0
        notification_count = 0
        res = 0
    except TypeError:
        check_count = 0
        inbox_count = 0
        notification_count = 0
        res = 0

    date_now = timezone.localtime()

    return locals()



