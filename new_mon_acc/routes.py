from new_mon_acc import app, db
from flask import render_template, redirect, url_for, flash, request
from new_mon_acc.forms import SignUpForm, SignInForm, AddCatForm, AddNoteForm, CreateReportForm, ResetPasswordRequestForm, \
    ResetPasswordForm
from new_mon_acc.models import User, Category, History
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, date
from new_mon_acc.utils import prepare_data, create_pie
from threading import Thread
from new_mon_acc.email import send_mail
import os


@app.route('/')
def root():
    return render_template('root.html', title='Welcome')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.date_created.desc()).all()
    page = request.args.get('page', 1, type=int)
    history = History.query.filter_by(user_id=current_user.id).order_by(History.date.desc()).paginate(page=page,
                                                                                                      per_page=5)
    form = CreateReportForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            out_dict = prepare_data(user_id=current_user.id, start_date=form.start.data, finish_date=form.finish.data)
            try:
                if not current_user.latest_report == 'default.png':
                    path_to_delete = os.path.join(app.root_path, 'static/', current_user.latest_report)
                    os.remove(path_to_delete)
            except:
                pass
            Thread(target=create_pie, args=[out_dict]).run()
            db.session.commit()
            return render_template('main.html', title='Home', categories=categories, history=history, form=form)
    else:
        form.start.data = datetime.utcnow()
        form.finish.data = datetime.utcnow()
    return render_template('main.html', title='Home', categories=categories, history=history, form=form)


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        category_by_default = Category(name='Other', user=new_user)
        db.session.add(new_user)
        db.session.add(category_by_default)
        db.session.commit()
        flash('Your account has been created, now you can log in', 'success')
        return redirect(url_for('sign_in'))
    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if check_password_hash(user.password, form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('home'))
        else:
            flash('Email or password incorrect, please check it', 'danger')
            return redirect(url_for('sign_in'))
    return render_template('signin.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('root'))


@app.route('/add_cat', methods=['GET', 'POST'])
@login_required
def add_cat():
    form = AddCatForm()
    if form.validate_on_submit():
        new_cat = Category(name=form.name.data, user_id=current_user.id)
        db.session.add(new_cat)
        db.session.commit()
        flash('Your category has been created', 'success')
        return redirect(url_for('home'))
    return render_template('addcat.html', title='Add Category', form=form)


@app.route('/delete/<category_id>', methods=['GET', 'POST'])
@login_required
def delete_cat(category_id):
    category = Category.query.get(category_id)
    other = Category.query.filter_by(user_id=current_user.id).filter_by(name='Other').first()
    history_cat = History.query.filter_by(category_id=category.id).all()
    for note in history_cat:
        note.category = other
        other.sum += note.spend
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add_note/<category_id>', methods=['GET', 'POST'])
@login_required
def add_note(category_id):
    category = Category.query.get(category_id)
    form = AddNoteForm()
    if form.validate_on_submit():
        new_note = History(user_id=current_user.id, category_id=category_id, spend=form.spend.data)
        category.sum += float(form.spend.data)
        db.session.add(new_note)
        db.session.commit()
        flash('Note has been added', 'success')
        return redirect(url_for('home'))
    return render_template('addnote.html', title='Add Note', form=form)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail.delay(subject='Money Accounting | Reset Password', sender=app.config['MAIL_USERNAME'],
                    recipients=[user.email],
                    text_body=render_template('reset_password.txt', user=user, token=token),
                    html_body=render_template('reset_password.html', user=user, token=token))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password', 'info')
            return redirect(url_for('sign_in'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('root'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been reset', 'success')
        return redirect('login')
    return render_template('reset_pw.html', title='Reset Password', form=form)
