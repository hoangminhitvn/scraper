import csv
import sys

"""
command to run : python tools/compare_csv.py file1.csv file2.csv
Compare provider_id between file1.csv and file2.csv
"""


class Provider:
    def __init__(self,provider_id, config_file=None):
        self.provider_id = provider_id.strip()
        self.config_file = config_file

    def compare(self, provider):
        return self.provider_id == provider.provider_id

    def to_string(self):
        return "%s, %s " % (self.provider_id, self.config_file)


class ProviderList:
    def __init__(self, file_name):
        self.file_name = file_name
        self.providers = []
        with open(file_name, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                config_file = [i for i in row if '.json' in i]
                config_file = config_file[0] if len(config_file) == 1 else None
                self.providers.append(Provider(row[0], row[1], config_file))


    def is_found(self, provider):
        for p in self.providers:
            if p.compare(provider):
                return True
        return False

    def contains_config_file(self):
        return self.providers[1].config_file is not None


provider1 = ProviderList(sys.argv[1])
provider2 = ProviderList(sys.argv[2])
my_providers = provider1 if provider1.contains_config_file() else provider2
clients_providers = provider2 if provider1.contains_config_file() else provider1
print provider2.contains_config_file()
not_found = []
for p in my_providers.providers:
    if not clients_providers.is_found(p):
        print p.to_string()
