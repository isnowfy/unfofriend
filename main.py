from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from auth import getauth,OAuth,OAuthCallback,OAuthLogout
import tweepy
import diff
import refresh

class MainPage(webapp.RequestHandler):
    def get(self):
        if users.get_current_user() is None:
            url = users.create_login_url(self.request.uri)
            self.response.out.write("<a href='"+url+"'>Google Login</a>\n")
        else:
            self.redirect('/home')
      

class Find(webapp.RequestHandler):
    def post(self):
        name=users.get_current_user()
        diff.Diff(getauth(name),tweepy.API(getauth(name)).me().screen_name,1,0,name);
        self.redirect('/home')

class Clear(webapp.RequestHandler):
    def post(self):
        name=users.get_current_user()
        diff.Diff(getauth(name),tweepy.API(getauth(name)).me().screen_name,1,1,name);
        self.redirect('/home')
      
class Home(webapp.RequestHandler):
    def get(self):  
        self.response.out.write("<html><head></head><body>")  
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            self.response.out.write("<a href='"+url+"'>%s Google Logout</a><br /><br />\n"%(users.get_current_user()))
        else:
            self.redirect('/')
        auth=getauth(users.get_current_user())
        if auth:
            user_name=tweepy.API(auth).me().screen_name
            self.response.out.write("<a href='/oauth_logout'>%s OAuth Logout</a><br /><br />\n"%user_name)
            if tweepy.API(auth).test():
                self.response.out.write("""
                <table>
                    <td>
                        <form action="/set" method="post">
                        <div><input type="submit" value="refresh"></div>
                        </form>
                    </td><td>
                        <form action="/clear" method="post">
                        <div><input type="submit" value="clear"></div>
                        </form>
                    </td>
                </table>""") 
                diff.Diff(auth,user_name,1,0,users.get_current_user());
                tmp=db.GqlQuery('SELECT * FROM Show WHERE name=:1',user_name)
                datatmp=[]
                for j in tmp:
                    datatmp=j
                self.response.out.write('<p><font color="#FF0000">new unfo:</font></p>')
                for i in datatmp.unfo:
                    self.response.out.write(i+'</br>')
                self.response.out.write('<p><font color="#FF0000">new fo:</font></p>')
                for i in datatmp.fo:
                    self.response.out.write(i+'</br>')       
            else:
                self.response.out.write('OAuth Error.<br />\n')
        else:
            self.response.out.write("<a href='/auth'>OAuth Login</a>\n")
        self.response.out.write("</body></html>")   


application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/home', Home),
  ('/auth', OAuth),
  ('/callback', OAuthCallback),
  ('/oauth_logout', OAuthLogout),
  ('/set', Find),
  ('/clear', Clear),
  ('/refresh', refresh.Refresh)
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
