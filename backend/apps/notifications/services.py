from .models import Notification


def notify(*, recipient, school, title, body="", notification_type=Notification.Type.SYSTEM, link=""):
    return Notification.objects.create(
        recipient=recipient,
        school=school,
        title=title,
        body=body,
        notification_type=notification_type,
        link=link,
    )


def notify_many(*, recipients, school, title, body="", notification_type=Notification.Type.SYSTEM, link=""):
    return Notification.objects.bulk_create([
        Notification(
            recipient=recipient,
            school=school,
            title=title,
            body=body,
            notification_type=notification_type,
            link=link,
        )
        for recipient in recipients
    ])
