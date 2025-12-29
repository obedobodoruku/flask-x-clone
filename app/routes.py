from flask import redirect, render_template, request, url_for, flash
from app import app, bcrypt
from app.models import db, User, Post, Reply
from datetime import datetime
from app.forms import RegistrationForm, LoginForm, CreatePostForm, UpdateAccountForm, ReplyForm, UpdatePostForm, UpdateReplyForm
from flask_login import login_required, login_user, logout_user ,current_user

@app.route("/", methods=["GET", "POST"])
def index():
    posts = Post.query.all()
    return render_template("home.html", title="Home Page", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully, you can now login.")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Hi!, {current_user.username}.")
            return redirect(url_for("index"))
        else:
            flash("Login unsuccessful, please check email and password")
    return render_template("login.html", title="Login Page", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/new_post", methods=["GET", "POST"])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(content=form.content.data, date_posted=datetime.utcnow(), user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Your Post has been sent")
        return redirect(url_for("index"))
    return render_template("create_post.html", title="New Post", form=form)

@app.route("/<username>/posts", methods=["GET"])
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    users_post = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).all()
    return render_template("user_post.html", users_post=users_post, user=user, title=f"{user.username}  Posts")

@app.route("/user", methods=["GET", "POST"])
@login_required
def account():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = Post.query.filter_by(user=user).all()
    return render_template("account.html",user=user, posts=posts, title=f"{current_user.username}'s Account", )

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.name = form.name.data
        db.session.commit()
        flash("Your Account has been Updated")
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = current_user.name
    return render_template("edit_profile.html", form=form, title=f"{current_user.username}'s Account")

@app.route("/<username>/post/<int:post_id>", methods=["GET", "POST"])
def view_post(username, post_id):
    form = ReplyForm()
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(id=post_id, user_id=user.id).first_or_404()
    replies = Reply.query.filter_by(post_id=post.id).all()
    return render_template("post.html",post=post, form=form, replies=replies, title=f"{user.username}'s post {post.id}")

@app.route("/post/<int:post_id>/reply", methods=["POST"])
def create_reply(post_id):
    form = ReplyForm()
    if form.validate_on_submit():
        post = Post.query.get_or_404(post_id)
        new_reply = Reply(content=form.content.data, user_id=current_user.id, post_id=post.id)
        db.session.add(new_reply)
        db.session.commit()
    return redirect(url_for("view_post", username=post.user.username, post_id=post.id))

@app.route("/delete_post/<int:post_id>", methods=["GET"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index", post_id=post.id))

@app.route("/update_post/<int:post_id>", methods=["GET", "POST"])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = UpdatePostForm()
    if form.validate_on_submit():
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for("view_post", username=post.user.username, post_id=post.id))
    elif request.method == "GET":
        form.content.data = post.content
    return render_template("update_post.html",post=post, form=form, title=f"Post {post.id} Update")

    
@app.route("/<int:post_id>/delete_reply/<int:reply_id>", methods=["GET"])
def delete_reply(post_id, reply_id):
    post = Post.query.get_or_404(post_id)
    reply = Reply.query.get_or_404(reply_id)
    db.session.delete(reply)
    db.session.commit()
    return redirect(url_for("view_post", username=post.user.username, post_id=post.id, reply_id=reply.id))

@app.route("/<int:post_id>/update_reply/<int:reply_id>", methods=["GET", "POST"])
def update_reply(post_id, reply_id):
    post = Post.query.get_or_404(post_id)
    reply = Reply.query.get_or_404(reply_id)
    form = UpdateReplyForm()
    if form.validate_on_submit():
        reply.content = form.content.data
        db.session.commit()
        return redirect(url_for("view_post",username=post.user.username, post_id=post.id))
    elif request.method == "GET":
        form.content.data = reply.content
    return render_template("update_reply.html", post=post, reply=reply, form=form, title=f"{reply.user.username}'s reply {reply.id} Update")

@app.route("/posts/<int:post_id>/reply/<int:reply_id>", methods=["GET", "POST"])
def view_reply(post_id, reply_id):
    form = ReplyForm()
    post = Post.query.get_or_404(post_id)
    reply = Reply.query.filter_by(id=reply_id, post_id=post_id).first_or_404()
    return render_template("reply.html", post=post, reply=reply, form=form)