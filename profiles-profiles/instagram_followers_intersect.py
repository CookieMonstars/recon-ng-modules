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
        'description': 'Retrieves all users who follow more than one user in the set.',
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

        follower_users = {}
        for username in usernames:
            self.output('Retrieving followers for %s' % username)
            profile = instaloader.Profile.from_username(L.context, username)
            for follower in profile.get_followers():
                self.output('Recording %s' % follower.username)
                if follower.username not in follower_users:
                    follower_users[follower.username] = []
                follower_users[follower.username].append(username)

        for follower, users in follower_users.items():
            if len(users) > 1:
                self.insert_profiles(
                    username=follower, 
                    resource='Instagram', 
                    category='social',
                    url='https://www.instagram.com/%s' % follower, 
                    notes=', '.join(users))