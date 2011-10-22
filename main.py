from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from auth import getauth,OAuth,OAuthCallback,OAuthLogout
import tweepy
import diff

class MainPage(webapp.RequestHandler):
  def get(self):
    if users.get_current_user() is None:
      url = users.create_login_url(self.request.uri)
      self.response.out.write("<a href='"+url+"'>Google Login</a>\n")
    else:
      self.redirect('/home')
      

class Find(webapp.RequestHandler):
  def post(self):
    diff.Diff(getauth(),users.get_current_user(),1);
    self.redirect('/home')
      
class Home(webapp.RequestHandler):
  def get(self):    
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      self.response.out.write("<a href='"+url+"'>Google Logout</a>\n")
    else:
      self.redirect('/')
    auth=getauth()
    user_name=users.get_current_user()
    if auth:
      self.response.out.write("<a href='/oauth_logout'>OAuth Logout</a><br /><br />\n")
      if tweepy.API(auth).test():
        tmp=diff.Diff(auth,user_name,0);
        self.response.out.write('<p><font color="#FF0000">new %d unfo:</font></p>'%len(tmp.unfo))
        for i in tmp.unfo:
            self.response.out.write(i+'</br>')
        self.response.out.write('<p><font color="#FF0000">new %d fo:</font></p>'%len(tmp.fo))
       # for i in s1:
       #     self.response.out.write(i+'</br>')
        self.response.out.write("""
          <form action="/set" method="post">
            <div><input type="submit" value="set"></div>
          </form>
        </body>
        when you push the set button,it will record your followers's list
        </br>
        and show the difference from the record and the current list 
      </html>""")          
      else:
        self.response.out.write('OAuth Error.<br />\n')
    else:
      self.response.out.write("<a href='/auth'>OAuth Login</a>\n")


application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/home', Home),
  ('/auth', OAuth),
  ('/callback', OAuthCallback),
  ('/oauth_logout', OAuthLogout),
  ('/set', Find)
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
