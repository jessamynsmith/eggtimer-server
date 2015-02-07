import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.template import Context

from eggtimer.apps.periods import models as period_models
from eggtimer.libs import email_sender


class Command(BaseCommand):
    help = 'Notify users of upcoming periods'

    def handle(self, *args, **options):
        users = period_models.User.objects.filter(
            periods__isnull=False, statistics__isnull=False).exclude(
            send_emails=False).distinct()
        for user in users:
            expected_in = (user.statistics.average_cycle_length
                           - user.statistics.current_cycle_length)
            expected_abs = abs(expected_in)
            expected_date = period_models._today() + datetime.timedelta(
                days=expected_in)
            formatted_date = expected_date.strftime('%B %d, %Y')
            if expected_abs == 1:
                day = 'day'
            else:
                day = 'days'

            context = Context({
                'full_name': user.get_full_name(),
                'expected_in': expected_abs,
                'day': day,
                'expected_date': formatted_date,
                'site_name': settings.ADMINS[0][0]
            })

            subject = ''
            if expected_in < 0:
                subject = "Period was expected %s %s ago" % (expected_abs, day)
                template_name = 'expected_ago'
            elif expected_in == 0:
                subject = "Period today!"
                template_name = 'expected_now'
            elif expected_in < 4:
                subject = "Period expected in %s %s" % (expected_in, day)
                template_name = 'expected_in'
            elif expected_in == 14:
                subject = "Ovulation today!"
                template_name = 'ovulating'
            if subject:
                plaintext = get_template('email/%s.txt' % template_name)
                email_sender.send(user, subject, plaintext.render(context), None)
