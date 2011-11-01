from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import mail
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
      

class MailSave(webapp.RequestHandler):
    def post(self):
        user_address=self.request.get("email")
        if not mail.is_email_valid(user_address):
            self.response.out.write("email address invalid!!!")
        else:
            name=str(users.get_current_user())
            showtmp=diff.getemail(name)
            showtmp.name=name
            showtmp.email=user_address
            showtmp.put()
            self.redirect('/home')

class Clear(webapp.RequestHandler):
    def post(self):
        name=users.get_current_user()
        diff.Diff(getauth(name),tweepy.API(getauth(name)).me().screen_name,1,1,name);
        self.redirect('/home')
      
class Home(webapp.RequestHandler):
    def get(self):  
        login_name=str(users.get_current_user())
        self.response.out.write("<html><head></head><body>")  
        if login_name:
            url = users.create_logout_url(self.request.uri)
            self.response.out.write("<a href='"+url+"'>%s Google Logout</a><br /><br />\n"%(login_name))
        else:
            self.redirect('/')
        auth=getauth(login_name)
        if auth:
            user_name=tweepy.API(auth).me().screen_name
            showtmp=diff.getemail(login_name).email
            self.response.out.write("<a href='/oauth_logout'>%s OAuth Logout</a><br /><br />\n"%user_name)
            if tweepy.API(auth).test():
                self.response.out.write("""
                <font color="#FF0000">if you put your email below,when you get new unfo i will send email to you</font>
                <table>
                    <tr>
                        <form action="/set" method="post">
                        <td><input type="text" name="email" size="20" value="%s"></td>
                        <td><input type="submit" value="save the email"></td>
                        </form>
                    </tr><br /><tr>
                        <form action="/clear" method="post">
                        <div><input type="submit" value="clear all the data"></div>
                        </form>
                    </tr>
                </table>"""%showtmp) 
                diff.Diff(auth,user_name,1,0,login_name);
                tmp=db.GqlQuery('SELECT * FROM Show WHERE name=:1',user_name)
                datatmp=[]
                for j in tmp:
                    datatmp=j
                self.response.out.write('<p><font color="#FF0000">new unfo:</font></p>')
                datatmp.unfo.reverse()
                for i in datatmp.unfo:
                    self.response.out.write(i+'</br>')
                self.response.out.write('<p><font color="#FF0000">new fo:</font></p>')
                datatmp.fo.reverse()
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
  ('/set', MailSave),
  ('/clear', Clear),
  ('/refresh', refresh.Refresh)
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
