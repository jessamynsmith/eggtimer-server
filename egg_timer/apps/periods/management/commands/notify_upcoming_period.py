import datetime
from django.core.management.base import BaseCommand

from egg_timer.apps.userprofiles import models as userprofile_models
from egg_timer.libs.email import send_email


class Command(BaseCommand):
    help = 'Notify users of upcoming periods'

    def handle(self, *args, **options):
        users = userprofile_models.UserProfile.objects.filter(
            periods__isnull=False).filter(statistics__isnull=False).distinct()
        for user in users:
            if not user.statistics.average_cycle_length:
                continue
            expected_in = user.statistics.average_cycle_length - user.statistics.current_cycle_length
            subject = ''
            if abs(expected_in) == 1:
                day = 'day'
            else:
                day = 'days'
            expected_date = datetime.date.today() + datetime.timedelta(days=expected_in)
            formatted_date = expected_date.strftime('%B %d, %Y')
            if expected_in < 0:
                subject = "Period was expected %s %s ago" % (abs(expected_in), day)
                text_body = "You should have gotten your period %s %s ago, on %s. Did you forget to add your last period?" % (abs(expected_in), day, formatted_date)
            elif expected_in == 0:
                subject = "Period today!"
                text_body = "You should be getting your period today!"
            elif expected_in < 4:
                subject = "Period expected in %s %s" % (expected_in, day)
                text_body = "You should be getting your period in %s %s, on %s." % (expected_in, day, formatted_date)
            if subject:
                send_email(user, subject, text_body, None)


