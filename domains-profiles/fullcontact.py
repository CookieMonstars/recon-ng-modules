from recon.core.module import BaseModule
from fullcontact import FullContactClient

class Module(BaseModule):

    meta = {
        'name': 'FullContact Domain Analyser',
        'author': 'Mike Jewell (@mikejewell)',
        'version': '1.0',
        'description': 'Harvests company profiles from the fullcontact.com API using domains'
                       'as input. Updates the \'profiles\' tables with the results.',
        'dependencies': ['fullcontact'],
        'required_keys': ['fullcontact_api'],
        'query': "SELECT DISTINCT domain FROM domains WHERE domain IS NOT NULL COLLATE NOCASE",
    }

    def module_run(self, domains):
        account = self.keys.get('fullcontact_api')
        client = FullContactClient(account)

        for domain in domains:
            company = client.company.enrich(domain=domain)

            details = company.get_details()
            if 'profiles' in details:
                for profile in details['profiles'].values():
                    self.insert_profiles(
                        username=profile['username'],
                        resource=profile['service'],
                        category='social',
                        url=profile['url'],
                        notes=domain,
                    )