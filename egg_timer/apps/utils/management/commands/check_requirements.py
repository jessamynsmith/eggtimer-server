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

    def _convert_to_dict(self, values_list):
        values_dict = {}
        for value in values_list:
            if value.strip() == '':
                continue
            value_tuple = value.split('==')
            if len(value_tuple) > 1:
                dict_value = value_tuple[1]
            else:
                dict_value = ''
                print "Library '%s' does not have a version specified. Consider pinning it to a specific version." % value_tuple[0]
            values_dict[value_tuple[0]] = dict_value
        return values_dict

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

        freeze_dict = self._convert_to_dict(freeze_results)
        req_dict = self._convert_to_dict(req_list)

        for freeze_key in freeze_dict:
            if check_prod and freeze_key == 'distribute':
                # heroku adds distribute, so ignore it in the prod list
                continue
            if freeze_key not in req_dict.keys():
                print "Item is missing from requirements files: %s==%s" % (freeze_key, freeze_dict[freeze_key])
            elif freeze_dict[freeze_key] != req_dict[freeze_key]:
                print "Mismatched versions for '%s'. Installed: %s, required: %s" % (freeze_key, freeze_dict[freeze_key], req_dict[freeze_key])

        for req_key in req_dict:
            if req_key not in freeze_dict.keys():
                print "Required item is not installed: %s==%s" % (req_key, req_dict[req_key])
