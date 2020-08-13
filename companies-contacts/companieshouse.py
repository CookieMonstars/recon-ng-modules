from recon.core.module import BaseModule
import requests

class Module(BaseModule):

    meta = {
        'name': 'Companies House Officers Fetcher',
        'author': 'Mike Jewell (@mikejewell)',
        'version': '1.0',
        'description': 'Harvests company officer contacts from Companies House using companies'
                       'as input. Updates the \'contacts\' tables with the results.',
        'required_keys': ['companieshouse_api'],
        'query': "SELECT DISTINCT company FROM companies WHERE company IS NOT NULL COLLATE NOCASE",
    }

    def parse_name(self, name):
        # Last name is capitalised at start, with comma delimiting
        pieces = name.split(',')
        last_name = pieces[0].capitalize()
        remaining = pieces[1].strip().split(' ')
        if len(remaining) == 1:
            first_name = remaining[0]
            middle_name = None
        else:
            first_name = remaining[0]
            middle_name = remaining[1] # Ignore other names
        return (first_name, middle_name, last_name)

    def module_run(self, companies):
        account = self.keys.get('companieshouse_api')

        for company in companies:
            resp = requests.get('https://api.companieshouse.gov.uk/search/companies?q=%s' % company, auth=(account,''))
            for item in resp.json()['items']:
                company_number = item['company_number']
                officers = requests.get('https://api.companieshouse.gov.uk/company/%s/officers' % company_number, auth=(account,''))
                for officer in officers.json()['items']:
                    if ',' not in officer['name']:
                        # Typically a company
                        continue

                    (first_name, middle_name, last_name) = self.parse_name(officer['name'])
                    contact = {
                        'first_name': first_name,
                        'middle_name': middle_name,
                        'last_name': last_name,
                        'notes': company,
                    }

                    if 'address' in officer:
                        if 'country' in officer['address']:
                            contact['country'] = officer['address']['country']
                        if 'region' in officer['address']:
                            contact['region'] = officer['address']['region']
                        elif 'locality' in officer['address']:
                            contact['region'] = officer['address']['locality']

                    self.insert_contacts(**contact)