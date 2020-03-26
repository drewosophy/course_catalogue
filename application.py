#!/usr/bin/env python3

from flask import (
    g,
    Flask,
    render_template,
    url_for,
    make_response,
    request,
    redirect,
    jsonify,
    flash,
    Markup,
    session as login_session)
from flask_httpauth import HTTPTokenAuth
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import httplib2
import json
import random
import string

from functools import wraps

from google.oauth2 import id_token
from google.auth.transport import requests

# import CRUD operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from db_model import Base, User, Course, Categories

app = Flask(__name__)
app.secret_key = "some-secret-key"
auth = HTTPTokenAuth(scheme='Token')

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# engine = create_engine('sqlite:///catalogue.db',
#                        connect_args={'check_same_thread': False})
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# This decorator checks if the user is logged or not
def login_required(f):
    @wraps(f)
    def x(*args, **kwargs):
        if 'user_id' not in login_session:
            return redirect('/login')
        g.user = login_session['user_id']
        return f(*args, **kwargs)
    return x


@app.route('/')
def index():
    categories = session.query(Categories).all()
    courses = session.query(Course).order_by(Course.title.desc()).limit(10).all()
    return render_template(
        "index.html",
        categories=categories,
        courses=courses,
        CLIENT_ID=CLIENT_ID
        )


@app.route('/login')
def login():
    cur_state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in range(32))
    login_session['cur_state'] = cur_state
    return render_template('login.html', cur_state=cur_state,
                           CLIENT_ID=CLIENT_ID)


@app.route('/google-auth', methods=['POST'])
def google_auth():
    if request.args.get('state') != login_session['cur_state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data.decode("utf-8")
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(code, requests.Request(),
                                              CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid.
        # Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
    except ValueError:
        # Invalid token
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = code
    login_session['email'] = idinfo['email']

    # if the user id does not exist, make a new one
    user = (session.query(User)
            .filter_by(email=idinfo['email'])
            .first())
    if not user:
        newUser = User(name=idinfo["name"], profile_pic=idinfo["picture"],
                       email=idinfo["email"])
        session.add(newUser)
        session.commit()
        user = (session.query(User)
                .filter_by(email=idinfo['email'])
                .first())
    login_session['g_user_id'] = userid
    login_session['user_id'] = user.id
    return 'You are now logged in'


@app.route("/logout")
@login_required
def logout():
    if login_session.get('g_user_id') is not None:
        del login_session['g_user_id']
    if login_session.get('user_id') is not None:
        del login_session['user_id']
    if login_session.get('access_token') is not None:
        del login_session['access_token']
    if login_session.get('email') is not None:
        del login_session['email']
    return make_response(json.dumps('logout successful'), 200)


@app.route("/google-logout")
def google_logout():
    access_token = login_session.get('access_token')
    if access_token is None:
        # response = make_response
        # (json.dumps('Current user not connected.'), 401)
        return redirect(url_for("index"))

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print(result)

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['email']
        return redirect(url_for('index'))
    else:
        response = make_response(json.dumps('Failed to logout'), 400)
        return response


@app.route('/catalog.json')
def catalogJson():
    categories = session.query(Categories).all()
    courses = session.query(Course).all()
    catalog = [category.serialize for category in categories]
    for category in catalog:
        category['courses'] = [i.serialize for i in courses
                               if i.category_ref == category['id']]
    return jsonify({'catalog': catalog})


@app.route('/coursecatalogue/<string:course_category>')
def categoryPage(course_category):
    category = session.query(Categories).filter_by(name=course_category).first()
    if category is None:
        return redirect(url_for("index"))
    courses = session.query(Course).filter_by(category_ref=category.id)
    return render_template(
        "category.html",
        category=category,
        courses=courses,
        CLIENT_ID=CLIENT_ID
        )


@app.route('/coursecatalogue/<string:course_category>/<string:course_title>')
def coursePage(course_category, course_title):
    category = session.query(Categories).filter_by(name=course_category).first()
    if category is None:
        return redirect(url_for("index"))
    course = session.query(Course).filter_by(category_ref=category.id,
                                             title=course_title).first()
    if course is None:
        return redirect(url_for("index"))
    return render_template(
        "course.html",
        category=category,
        course=course,
        CLIENT_ID=CLIENT_ID
        )


@app.route('/coursecatalogue/new-course', methods=['GET', 'POST'])
@login_required
def newCourse():
    categories = session.query(Categories).all()
    if request.method == 'GET':
        return render_template('new-course.html', categories=categories, form={}, CLIENT_ID=CLIENT_ID)
    elif request.method == 'POST':
        category = session.query(Categories).filter_by(id=request.form['category']).first()
        if category is None:
            return render_template('new-course.html', errors={'category': "Category does not exists"},
                                   categories=categories, form=request.form,
                                   CLIENT_ID=CLIENT_ID
                                   )
        existing_course = session.query(Course).filter_by(title=request.form['title'], category_ref=category.id).first()
        if existing_course is not None:
            return render_template('new-course.html', errors={'title': "Course title has been taken"},
                                   categories=categories, form=request.form,
                                   CLIENT_ID=CLIENT_ID
                                   )
        course = Course(title=request.form['title'], description=request.form['description'],
                        duration=request.form['duration'], category_ref=category.id,
                        creator_ref=g.user
                        )
        session.add(course)
        session.commit()
        return redirect(url_for("coursePage", course_category=category.name, course_title=course.title))


@app.route('/coursecatalogue/<string:course_category>/<string:course_title>/edit', methods=['GET', 'POST'])
@login_required
def editCourse(course_category, course_title):
    category = session.query(Categories).filter_by(name=course_category).first()
    if category is None:
        return redirect(url_for("index"))
    course = session.query(Course).filter_by(category_ref=category.id,
                                             creator_ref=g.user, title=course_title).first()
    if course is None:
        return redirect(url_for("index"))

    categories = session.query(Categories).all()
    if request.method == 'GET':
        form = {
            'title': course.title,
            'description': course.description,
            'duration': course.duration,
            'category': course.category.id
        }
        return render_template('edit-course.html',  category=category, categories=categories,
                               course=course, form=form, CLIENT_ID=CLIENT_ID)
    if request.method == 'POST':
        category = session.query(Categories).filter_by(id=request.form['category']).first()
        if category is None:
            return render_template('edit-course.html', errors={'category': "Category does not exists"},
                                   categories=categories, form=request.form,
                                   course=course, category=category,
                                   CLIENT_ID=CLIENT_ID
                                   )
        course.title = request.form["title"]
        course.description = request.form["description"]
        course.duration = request.form["duration"]
        course.category_ref = request.form["category"]
        session.commit()
        return redirect(url_for("coursePage", course_category=category.name, course_title=course.title))


@app.route('/coursecatalogue/<string:course_category>/<string:course_title>/delete', methods=['GET', 'POST'])
@login_required
def deleteCourse(course_category, course_title):
    category = session.query(Categories).filter_by(name=course_category).first()
    if category is None:
        return redirect(url_for("index"))
        course = session.query(Course).filter_by(category_ref=category.id,
                                                 creator_ref=g.user,
                                                 title=course_title).first()
    if course is None:
        return redirect(url_for("index"))
    session.delete(course)
    session.commit()
    if request.method == 'GET':
        return render_template('delete-course.html',  category=category,
                               course=course, CLIENT_ID=CLIENT_ID)
    elif request.method == 'POST':
        return redirect(url_for("index"))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
