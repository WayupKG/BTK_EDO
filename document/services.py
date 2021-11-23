import transliterate

from django.utils.text import slugify


def gen_slug(number, name):
    world = ''
    try:
        for i in name.lower():
            if i == 'ң':
                world += 'н'
            elif i == 'ү':
                world += 'у'
            elif i == 'ө':
                world += 'о'
            else:
                world += i
        slug = transliterate.translit(f"{number}-{world}", reversed=True)
    except:
        slug = f"{number}-{name}"
    return slugify(slug, allow_unicode=True)


def create_number(id_doc):
    if id_doc < 10:
        reg_number = f'21БТК00{id_doc}'
    elif 10 <= id_doc < 100:
        reg_number = f'21БТК0{id_doc}'
    else:
        reg_number = f'21БТК{id_doc}'
    return reg_number


def create_notification(movement, appointment):
    if appointment == 'I_approve':
        body = f'Получено ответ: {movement.responsible.position} - {movement.responsible.get_full_name} утвердил документ с номером  - {movement.document.name}.'
    elif appointment == 'I_agree':
        body = f'Получено ответ: {movement.responsible.position} - {movement.responsible} согласен с документом под номером {movement.document.number} - {movement.document.name}.'
    elif appointment == 'I_dont_agree':
        body = f'Получено ответ: {movement.responsible.position} - {movement.responsible} не согласен с документом под номером {movement.document.number} - {movement.document.name}'
    elif appointment == 'Accepted_for_execution':
        body = f'Получено ответ: {movement.responsible.position} - {movement.responsible} принял к исполнению документ с номером {movement.document.number} - {movement.document.name}'
    elif appointment == 'Noted':
        body = f'Получено ответ: {movement.responsible.position} - {movement.responsible} принял к сведенью документ с номером {movement.document.number} - {movement.document.name}'
    else:
        body = f'NotificationErrors - {movement.document.number}'
    return body


def upload_to_file(instance, filename):
    list_file = filename.split('.')
    return f'Documents/{instance.document.author.account.username}/{instance.document.number}/' \
           f'{instance.document.number}-{list_file[0]}.{list_file[-1]}/'


def upload_to_reply_file(instance, filename):
    list_file = filename.split('.')
    return f'Reply/{instance.reply.document.author.account.username}/{instance.reply.document.number}/' \
           f'{list_file[0]}-{instance.reply.document.number}.{list_file[-1]}/'



STATUS = (('Done', 'Выполнено'), ('Not_completed', 'Не выполнено'), ('In_process', 'В процессе'))

STATUS_STATEMENT = (('Submitted', 'Подано'), ('Approved', 'Утверждено'), ('Rejected', 'Отклонено'), ('Done', 'Выполнено'))

REPLY_STATUS = (('To_accept', 'Принять'), ('Not_accepted', 'Не принять'), ('Waiting', 'В ожидании'))

TYPE = (('Statement', 'Заявление'), ('Raport', 'Рапорт'))

PURPOSES = (
    ('For_approval', 'На утверждение'),
    ('For_agreement', 'На согласование'),
    ('To_be_executed', 'К исполнению'),
    ('For_your_information', 'К сведению'),
)

APPOINTMENT = (
    ('I_approve', 'Утверждаю'),
    ('I_agree', 'Согласен'),
    ('I_dont_agree', 'Не согласен'),
    ('Accepted_for_execution', 'Принято к исполнению'),
    ('Noted', 'Принято к сведению'),
    ('Waiting', 'В ожидании')
)

