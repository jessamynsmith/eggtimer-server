import datetime
from django.core.management.base import BaseCommand

from egg_timer.apps.userprofiles import models as userprofile_models
from egg_timer.libs.email import send_email


class Command(BaseCommand):
    help = 'Notify users of upcoming periods'

    def handle(self, *args, **options):
        today = datetime.date.today()
        users = userprofile_models.UserProfile.objects.filter(
            periods__isnull=False).filter(statistics__isnull=False).distinct()
        for user in users:
            last_period = user.periods.order_by('-start_date')[0]
            days_since_last = (today - last_period.start_date).days
            if not user.statistics.average_cycle_length:
                continue
            expected_in = user.statistics.average_cycle_length - days_since_last
            if expected_in < 0:
                subject = "Period was expected %s days ago" % (abs(expected_in))
                text_body = "You should have gotten your period %s days ago. Did you forget to add a period?"
                send_email(user, subject, text_body, None)
            elif expected_in < 4:
                subject = "Period expected in %s days" % expected_in
                text_body = "You should be getting your period in %s days."
                send_email(user, subject, text_body, None)


