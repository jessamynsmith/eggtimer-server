import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Ensure that all installed packages are in requirements.txt'

    def handle(self, *args, **options):
        proc = subprocess.Popen(['pip', 'freeze'], stdout=subprocess.PIPE)
        freeze_results = proc.communicate()[0].split('\n')

        common_file = open('requirements/common.txt')
        reqs = common_file.read()
        common_file.close()
        req_list = reqs.split('\n')

        dev_file = open('requirements/dev.txt')
        reqs = dev_file.read()
        dev_file.close()
        req_list.extend(reqs.split('\n')[1:])

        sorted(freeze_results)
        sorted(req_list)

        for freeze_item in freeze_results:
            if freeze_item not in req_list:
                print "Item is missing from requirements files: %s" % freeze_item
