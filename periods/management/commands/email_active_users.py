from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.template.loader import get_template
from django.template import Context

from periods import models as period_models, email_sender


class Command(NoArgsCommand):
    help = 'Email all active users'

    option_list = NoArgsCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
                    help='Tells Django to NOT prompt the user for input of any kind.'),
    )

    def handle(self, *args, **options):
        interactive = options.get('interactive')

        users = period_models.User.objects.filter(
            is_active=True, flow_events__isnull=False, statistics__isnull=False).exclude(
            send_emails=False).distinct()
        active_users = []
        for user in users:
            # Don't email users who haven't tracked a period in over 3 months
            if user.statistics.current_cycle_length < 90:
                active_users.append(user)

        if interactive:
            confirm = input("""You are about to email %s users about their accounts.
Are you sure you want to do this?

    Type 'yes' to continue, or 'no' to cancel: """ % len(active_users))
        else:
            confirm = 'yes'

        if confirm == 'yes':
            subject = 'Important information about the data in your eggtimer account'
            template_name = 'notification'
            context = Context({})
            plaintext = get_template('periods/email/%s.txt' % template_name)
            for user in active_users:
                email_sender.send(user, subject, plaintext.render(context), None)
        else:
            print("Would have emailed the following %s users:\n-------------------------"
                  % len(active_users))
            for user in active_users:
                print("%35s %5s periods" % (user.email, user.flow_events.count()))
