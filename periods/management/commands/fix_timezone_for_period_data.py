from optparse import make_option
import pytz

from django.core.management.base import NoArgsCommand

from periods import models as period_models


class Command(NoArgsCommand):
    help = 'Update FlowEvent data to match User timezone'

    option_list = NoArgsCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
                    help='Tells Django to NOT prompt the user for input of any kind.'),
    )

    def handle(self, *args, **options):
        interactive = options.get('interactive')

        users = period_models.User.objects.filter(
            flow_events__isnull=False).distinct()

        if interactive:
            users_info = ['\t%s (%s)' % (user.email, user.timezone) for user in users]
            confirm = input("""You are about to update flow events for the following users:\n%s
Are you sure you want to do this?

    Type 'yes' to continue, or 'no' to cancel: """ % "\n".join(users_info))
        else:
            confirm = 'yes'

        for user in users:
            user_timezone = pytz.timezone(user._timezone.zone)
            print("User: %s (%s)" % (user.email, user_timezone))
            for flow_event in user.flow_events.all().order_by('timestamp'):
                timestamp = flow_event.timestamp
                utc_timestamp = timestamp.astimezone(pytz.utc)
                if confirm == 'yes':
                    flow_event.timestamp = utc_timestamp
                    flow_event.save()
                else:
                    print("\t%s -> %s" % (flow_event.timestamp, utc_timestamp))
