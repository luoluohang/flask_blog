import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or "hard to guess string"
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	MAIL_SERVER = 'smtp.163.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = 'lqh2541@163.com'
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
	FLASKY_MAIL_SENDER = 'lqh2541@163.com'
	FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
	FLASKY_POSTS_PER_PAGE = 20
	FLASKY_FOLLOWERS_PER_PAGE = 20
	FLASKY_COMMENTS_PER_PAGE = 20
	@staticmethod
	def init_app(app):
		pass
	
class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI =\
    'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

config = {'development':DevelopmentConfig,'default': DevelopmentConfig}
	