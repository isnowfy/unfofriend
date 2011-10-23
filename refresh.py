from google.appengine.ext import db
from google.appengine.ext import webapp
import diff
from auth import getauth

class Refresh(webapp.RequestHandler):
    def get(self): 
        tmp=db.GqlQuery('SELECT * FROM Friend')
        for i in tmp:
            diff.Diff(getauth(i.login_name),i.name,1,0,i.login_name);