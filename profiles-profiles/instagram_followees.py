# module required for framework integration
from recon.core.module import BaseModule
# mixins for desired functionality
from recon.mixins.resolver import ResolverMixin
from recon.mixins.threads import ThreadingMixin
# module specific imports
import instaloader

class Module(BaseModule, ResolverMixin, ThreadingMixin):

    meta = {
        'name': 'Instagram Followees',
        'author': 'Mike Jewell (@mikejewell)',
        'version': '1.0',
        'description': 'Retrieves all followees of an Instagram account.',
        'dependencies': ['instaloader'],
        'required_keys': ['instagram_account'],
        'comments': (
            'Before using this module, you need to run `instaloader --login your_username` and then set instagram_account to your_username.',
        ),
        'query': "SELECT DISTINCT username FROM profiles WHERE username IS NOT NULL AND resource LIKE 'Instagram' COLLATE NOCASE",
    }

    # mandatory method
    # the second parameter is required to capture the result of the "SOURCE" option, which means that it is only required if "query" is defined within "meta"
    # the third parameter is required if a value is returned from the "module_pre" method
    def module_run(self, usernames):
        account = self.keys.get('instagram_account')
        L = instaloader.Instaloader()
        L.load_session_from_file(account)

        for username in usernames:
            profile = instaloader.Profile.from_username(L.context, username)
            for followee in profile.get_followees():
                self.insert_profiles(
                    username=followee.username, 
                    resource='Instagram', 
                    category='social',
                    url='https://www.instagram.com/%s' % followee.username, 
                    notes=username)