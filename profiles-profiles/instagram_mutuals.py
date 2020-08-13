from recon.core.module import BaseModule
from recon.mixins.resolver import ResolverMixin
from recon.mixins.threads import ThreadingMixin
import instaloader

class Module(BaseModule, ResolverMixin, ThreadingMixin):

    meta = {
        'name': 'Instagram Mutuals',
        'author': 'Mike Jewell (@mikejewell)',
        'version': '1.0',
        'description': 'Retrieves all mutual friends (followers and followees) of an Instagram account.',
        'dependencies': ['instaloader'],
        'required_keys': ['instagram_account'],
        'comments': (
            'Before using this module, you need to run `instaloader --login your_username` and then set instagram_account to your_username.',
        ),
        'query': "SELECT DISTINCT username FROM profiles WHERE username IS NOT NULL AND resource LIKE 'Instagram' COLLATE NOCASE",
    }

    def module_run(self, usernames):
        account = self.keys.get('instagram_account')
        L = instaloader.Instaloader()
        L.load_session_from_file(account)

        for username in usernames:
            profile = instaloader.Profile.from_username(L.context, username)
            known_followees = []
            for followee in profile.get_followees():
                known_followees.append(followee.username)
            for follower in profile.get_followers():
                if follower.username in known_followees:
                    self.insert_profiles(
                        username=follower.username, 
                        resource='Instagram', 
                        category='social',
                        url='https://www.instagram.com/%s' % follower.username, 
                        notes=username)
