from flask import render_template,redirect,request,url_for,flash
from . import user_m
from .forms import LoginForm,RegistrationForm
from ..models import User
from ..import db
from ..email import send_email
from flask.ext.login import login_user,logout_user,login_required,current_user

@user_m.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed \
		and request.endpoint[:7] != 'user_m.' \
		and request.endpoint != 'static':
			return redirect(url_for('user_m.unconfirmed'))

@user_m.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('user_m/unconfirmed.html')

@user_m.route('/login',methods = ['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid username or password.')
	return render_template('user_m/login.html',form = form)

@user_m.route('/logout')
@login_required
def logout():
	logout_user()
	flash('you have been logged out')
	return redirect(url_for('main.index'))
	
@user_m.route('/register',methods = ['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username = form.username.data,email = form.email.data,
		password = form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email,'confirm your account','mail/confirm',token = token,user = user)
		flash('an email has been sent to you by email')
		return redirect(url_for('.login'))
	return render_template('user_m/register.html',form = form)
	
@user_m.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account. Thanks!')
	else:
		flash('The confirmation link is invalid or has expired.')
	return redirect(url_for('main.index'))

@user_m.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email,'confirm your account','mail/confirm',token = token,user = current_user)
	flash('an new email has been sent to you by email')
	return redirect(url_for('main.index'))
	



	
	
		
	
	
	
	
	
	
	
	
	
	
			
