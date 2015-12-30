from . import main
from flask import render_template,redirect,abort,flash,url_for,abort,request,current_app,\
make_response
from ..models import User,Role,Permission,Post,Follow,Comment
from flask.ext.login import login_required,current_user
from .. import db
from .forms import EditProfileForm,EditProfileAdminForm,PostForm,CommentForm
from ..decorators import admin_required,permission_required
from ipdb import set_trace


@main.route('/',methods = ['GET','POST'])
def index():
	from utils import cheese
	cheese()
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
			post = Post(body = form.body.data,author_id = current_user.id)
			#post.on_changed_body()
			db.session.add(post)
			return redirect(url_for('.index'))
	page = request.args.get('page', 1, type=int)
	show_followed = False
	if current_user.is_authenticated:
		show_followed = bool(request.cookies.get('show_followed',''))
	if show_followed:
		query = current_user.followed_posts
	else:
		query = Post.query
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page,per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out=False)
	posts = pagination.items
	return render_template('index.html',form = form,posts = posts,
		show_followed = show_followed,pagination = pagination)
		

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		abort(404)
	page = request.args.get('page',1,type = int)
	pagination = user.post.order_by(Post.timestamp.desc()).paginate(page,
		per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out=False)
	posts = pagination.items
	return render_template('user.html',user = user,posts = posts,pagination = pagination)
	
@main.route('/user/<username>/edit_profile',methods = ['GET','POST'])
@login_required
def edit_profile(username):
	form = EditProfileForm();
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('you have changed your information successfully!')
		return redirect(url_for('.user',username = username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html',form = form)
	
@main.route('/edit_profile/<int:id>',methods = ['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash('The profile has been updated.')
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)
	
@main.route('/post/<int:id>',methods = ['GET','POST'])
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body = form.body.data, author = current_user._get_current_object(),
			 post = post)
		db.session.add(comment)
		flash('your comment has been published!')
		return redirect(url_for('.post',id = post.id,page = -1))
	page = request.args.get('page',1, type = int)
	if page == -1:
		page = (post.comments.count()-1)/current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page,
		per_page = current_app.config['FLASKY_COMMENTS_PER_PAGE'],error_out = False)
	comments = pagination.items
	return render_template('post.html',posts=[post],form = form, pagination = pagination,
		comments = comments)
	
@main.route('/edit/<int:id>',methods = ['GET','POST'])
def edit_post(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		flash('the post has been updated')
		return redirect(url_for('.post',id = post.id))
	form.body.data = post.body
	return render_template('edit_post.html',form = form)

@main.route('/delete/<int:id>')
def delete(id):
	post = Post.query.get_or_404(id)
	db.session.delete(post)
	flash('delete successfully!')
	return redirect(url_for('.index'))
	
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('Invalid user')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		current_user.unfollow(user)
		flash('you are now unfollowing %s.' % username)
	else:
		current_user.follow(user)
		flash('you are now following %s.' % username)
	return redirect(url_for('.user',username = username))

@main.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('Invalid user')
		return redirect(url_for('.index'))
	page = request.args.get('page',1,type= int )
	pagination = user.follower.paginate(page,
		per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out = False)
	follows = [{'user':item.followed,'timestamp':item.timestamp}
		for item in pagination.items]
	return render_template('followers.html', user = user,pagination = pagination, 
		title = 'Followers of', endpoint = '.followers',follows = follows)
		
@main.route('/followed_by/<username>')
def followed_by(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('Invalid user')
		return redirect(url_for('.index'))
	page = request.args.get('page',1,type = int)
	pagination = user.followed.paginate(page,
		per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out = False)
	follows = [{'user':item.follower,'timestamp':item.timestamp}
		for item in pagination.items]
	return render_template('followers.html',user = user,pagination = pagination,
		follows = follows,title = 'Followed by',endpoint = '.followed_by')
		
@main.route('/all')
@login_required
def show_all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed','',max_age = 30*24*60*60)
	return resp
	
@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed','1',max_age = 30*24*60*60)
	return resp
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page = request.args.get('page',1,type = int)
	pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page,
		per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
		error_out=False)
	comments = pagination.items
	return render_template('moderate.html',comments = comments,pagination = pagination,
		page = page)
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	return redirect(url_for('.moderate',page = request.args.get('page',1,type = int)))
	
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	return redirect(url_for('.moderate',page = request.args.get('page',1,type = int)))
	
	
	

		

		
	

	
	