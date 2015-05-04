import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.template import Context

from periods import models as period_models, email_sender


class Command(BaseCommand):
    help = 'Notify users of upcoming periods'

    def _format_date(self, date_value):
        return date_value.strftime('%A %B %d, %Y')

    def handle(self, *args, **options):
        users = period_models.User.objects.filter(
            flow_events__isnull=False, statistics__isnull=False).exclude(
            send_emails=False).distinct()
        for user in users:
            expected_in = (user.statistics.average_cycle_length
                           - user.statistics.current_cycle_length)
            expected_abs = abs(expected_in)
            today = period_models.today()
            expected_date = today + datetime.timedelta(
                days=expected_in)
            if expected_abs == 1:
                day = 'day'
            else:
                day = 'days'

            context = Context({
                'full_name': user.get_full_name(),
                'today': self._format_date(today),
                'expected_in': expected_abs,
                'day': day,
                'expected_date': self._format_date(expected_date),
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
            elif expected_in == user.luteal_phase_length:
                subject = "Ovulation today!"
                template_name = 'ovulating'
            if subject:
                plaintext = get_template('email/%s.txt' % template_name)
                email_sender.send(user, subject, plaintext.render(context), None)
