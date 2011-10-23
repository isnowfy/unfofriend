# coding: utf-8

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db
import tweepy

consumer_key = 'Ol4nbgy5QXejJMMO53p3Q'
consumer_secret = 'VQtFQ8dKEW4waEbwGBeFcWg6ZDpKKuPZvowLr9qSpTQ'
domain = 'https://unfofriend.appspot.com/'

class OAuthTokenDB(db.Model):
    oakey = db.StringProperty()
    secret = db.StringProperty()

def getauth(user_name=users.get_current_user()):
    if not user_name:return None
    user_name=str(user_name)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    oauth_token = OAuthTokenDB.get_by_key_name(key_names=user_name)
    if oauth_token is None:return None
    auth.set_access_token(oauth_token.oakey, oauth_token.secret)
    return auth

class OAuth(webapp.RequestHandler):
    def get(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret, domain + 'callback')
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            self.response.out.write('Error! Failed to get request token.')
            return
        user_name=str(users.get_current_user())
        oauth_token = OAuthTokenDB(key_name=user_name, oakey=auth.request_token.key, secret=auth.request_token.secret)
        oauth_token.put()
        self.redirect(redirect_url)

class OAuthCallback(webapp.RequestHandler):
    def get(self):
        verifier = self.request.get('oauth_verifier')
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        user_name=str(users.get_current_user())
        oauth_token = OAuthTokenDB.get_by_key_name(key_names=user_name)
        auth.set_request_token(oauth_token.oakey, oauth_token.secret)
        try:
            auth.get_access_token(verifier)
        except tweepy.TweepError:
            self.response.out.write('Error! Failed to get access token.')
            return
        user_name = str(users.get_current_user())
        oauth_token = OAuthTokenDB(key_name=user_name, oakey=auth.access_token.key, secret=auth.access_token.secret)
        oauth_token.put()
        self.redirect('/')

class OAuthLogout(webapp.RequestHandler):
    def get(self):
        user_name = str(users.get_current_user())
        oauth_token = OAuthTokenDB.get_by_key_name(key_names=user_name)
        if oauth_token:
            db.delete(oauth_token)
        self.redirect('/')
