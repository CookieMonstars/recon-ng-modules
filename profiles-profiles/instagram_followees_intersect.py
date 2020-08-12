# module required for framework integration
from recon.core.module import BaseModule
# mixins for desired functionality
from recon.mixins.resolver import ResolverMixin
from recon.mixins.threads import ThreadingMixin
# module specific imports
import instaloader

class Module(BaseModule, ResolverMixin, ThreadingMixin):

    meta = {
        'name': 'Instagram Followers Intersect',
        'author': 'Mike Jewell (@mikejewell)',
        'version': '1.0',
        'description': 'Retrieves all users who are followed by more than one user in the set.',
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

        followee_users = {}
        for username in usernames:
            self.output('Retrieving followees for %s' % username)
            profile = instaloader.Profile.from_username(L.context, username)
            for followee in profile.get_followees():
                self.output('Recording %s' % followee.username)
                if followee.username not in followee_users:
                    followee_users[followee.username] = []
                followee_users[followee.username].append(username)

        for followee, users in followee_users.items():
            if len(users) > 1:
                self.insert_profiles(
                    username=followee, 
                    resource='Instagram', 
                    category='social',
                    url='https://www.instagram.com/%s' % followee, 
                    notes=', '.join(users))