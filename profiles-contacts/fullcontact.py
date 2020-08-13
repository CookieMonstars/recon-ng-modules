from recon.core.module import BaseModule
from fullcontact import FullContactClient

class Module(BaseModule):

    meta = {
        'name': 'FullContact Profile Enricher',
        'author': 'Mike Jewell (@mikejewell)',
        'version': '1.0',
        'description': 'Harvests contacts from the fullcontact.com API using profiles'
                       'as input. Updates the \'contacts\' tables with the results.',
        'dependencies': ['fullcontact'],
        'required_keys': ['fullcontact_api'],
        'query': "SELECT DISTINCT username, url, resource FROM profiles WHERE resource IS NOT NULL COLLATE NOCASE",
    }

    def module_run(self, profiles):
        account = self.keys.get('fullcontact_api')
        client = FullContactClient(account)
        for (username, url, resource) in profiles:
            if url is not None:
                k = 'url'
                v = url
            elif username is not None:
                k = 'username'
                v = username
            else:
                continue

            result = client.person.enrich(
                profiles=[{'service':resource, k:v}])

            if result.get_status_code() != 200:
                continue

            if 'details' not in result.json():
                continue

            contact = {}
            details = result.json()['details']
            if 'locations' in details and len(details['locations']) > 0:
                if 'region' in details['locations'][0]:
                    contact['region'] = details['locations'][0]['region']
                if 'country' in details['locations'][0]:
                    contact['country'] = details['locations'][0]['country']
            if 'phones' in details and len(details['phones']) > 0:
                contact['phone'] = details['phones'][0]
            if 'name' in details:
                contact['first_name'] = details['name'].get('given', None)
                contact['last_name'] = details['name'].get('family', None)
            if 'emails' in details and len(details['emails']) > 0:
                contact['email'] = details['emails'][0]

            if len(contact) > 0:
                contact['notes'] = '%s %s %s' % (resource, k, v)
                self.insert_contacts(**contact)