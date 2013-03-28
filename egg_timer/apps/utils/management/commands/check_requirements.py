import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Ensure that all installed packages are in requirements.txt'

    def _get_file_contents(self, name):
        req_file = open('requirements/%s.txt' % name)
        reqs = req_file.read()
        req_file.close()
        req_list = reqs.split('\n')
        if req_list[0].startswith('-r'):
            req_list = req_list[1:]
        return req_list

    def handle(self, *args, **options):
        check_prod = False
        if len(args) == 1:
            if args[0] == 'prod':
                check_prod = True
            else:
                print "Unrecognized option %s; defaulting to checking dev requirements." % args[0]

        proc = subprocess.Popen(['pip', 'freeze'], stdout=subprocess.PIPE)
        freeze_results = proc.communicate()[0].split('\n')

        req_list = self._get_file_contents('common')

        if check_prod:
            req_list.extend(self._get_file_contents('prod'))
        else:
            req_list.extend(self._get_file_contents('dev'))

        sorted(freeze_results)
        sorted(req_list)

        for freeze_item in freeze_results:
            if freeze_item not in req_list:
                print "Item is missing from requirements files: %s" % freeze_item

        for req_item in req_list:
            if req_item not in freeze_results:
                print "Required item is not installed: %s" % req_item
