from flask import Flask, render_template, redirect, session, url_for, request, flash
from modules.create_db import create_db
from modules.DBConnect import DBConnect
from modules.config import ACCESS_LEVEL
from re import match

# Configuration
app = Flask(__name__)
app.config.from_object('modules.config')


# Route manager
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == 'POST':
        if len(request.form['source_link']) > 0:
            new_link = con.new_link(request.form['source_link'], request.form['access_level'],
                                    session['user']['id'] if 'user' in session else 0)
            return render_template('index.html', title="Link shortener", logged='user' in session,
                                   shortened_link=request.host_url + new_link)
        else:
            flash('Input a valid link', category='danger')
    return render_template('index.html', title="Link shortener", logged='user' in session)


@app.route('/register', methods=["POST", "GET"])
def sign_up():
    if 'user' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        if con.register_user(request.form['email'], request.form['password']):
            flash('Successful registration!', category='success')
            return redirect(url_for('sign_in'))
        flash('Incorrect input!', category='danger')
    return render_template('signup.html')


@app.route('/login', methods=["POST", "GET"])
def sign_in():
    if 'user' in session:
        return redirect(url_for('profile'))
    elif request.method == 'POST':
        if con.login(request.form['email'], request.form['password']):
            return redirect(url_for('profile'))
        else:
            flash('Incorrect input', category='danger')
    return render_template('signin.html')


@app.route('/profile', methods=["POST", "GET"])
def profile():
    if 'user' in session:
        if request.method == 'POST':
            if con.link_unique(request.form['new_link'], session['user']['id']):
                con.link_update(request.form['link_id'], request.form['new_link'], request.form['access_level'])
            else:
                flash('Shortname already taken', category='info')
        links = con.get_user_links(session['user']['id'])
        return render_template('profile.html', username=session['user']['email'], title="Profile",
                               logged='user' in session, user_links=links, access_level=ACCESS_LEVEL)
    else:
        return redirect(url_for('sign_in'))


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))


@app.route('/<shortened_link>')
def get_link(shortened_link):
    link = con.get_source_link(shortened_link)
    con.increment_visit_counter(link['id'])
    access_level = link['access_level']
    source_link = link['source_link']
    if not match(r'(http[s]*[:]{1}[\/]{2})', source_link):
        source_link = f'https://{source_link}'
    if access_level == 0:
        return redirect(source_link)
    elif access_level == 1:
        if 'user' in session:
            return redirect(source_link)
        else:
            flash('Link type: general. Following allowed only for authorized users', category='info')
            return redirect(url_for('sign_in'))
    elif access_level == 2:
        if 'user' in session and session['user']['id'] == link['user_created_id']:
            return redirect(source_link)
        else:
            flash('This is private link. Sign-in to confirm access.', category='info')
            return redirect(url_for('sign_in'))


@app.route('/delete/<shortened_link>')
def delete_link(shortened_link):
    link = con.get_source_link(shortened_link)
    if 'user' in session and link['user_created_id'] == session['user']['id']:
        con.link_delete(link['id'])
        flash('Link deleted successfully', category='success')
        return redirect(url_for('profile'))
    else:
        flash('You can delete only your links', category='dander')
        return redirect(url_for('sign_in'))


if __name__ == '__main__':
    create_db(app.config['DATABASE'], app.config['DBSCRIPT'])
    con = DBConnect(app.config['DATABASE'])
    app.run()
