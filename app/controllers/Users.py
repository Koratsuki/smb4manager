# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
"""

import os, json
from flask import url_for, jsonify, redirect, request, render_template, send_from_directory, flash, session

from app import app

from app.model.auth.AuthFlask import AuthFlask
auth = AuthFlask()

from app.model.UserModel import UserModel, User



@app.route('/users/')
@auth.login_required
def users():
    model = UserModel(session['username'],session['password'])
    users = model.GetUserList()
    newuserlist = []
    ico_active = '<span class="label label-success">Active</span>'
    ico_deactive = '<span class="label">Dective</span>'
    for user in users:
        if(user.username not in ['krbtgt','SMB$', 'dns-smb']):
              pass
              if (not user.fullname): user.fullname  = user.username
              newuserlist.append(user)


    return render_template('users.html', users=newuserlist, utils=session['utils'])



@app.route('/users/edit/<rid>', methods=["GET", "POST"])
@auth.login_required
def users_edit(rid):
    model = UserModel(session['username'],session['password'])
    user = model.GetUser(int(rid))
    return render_template('users_edit.html', utils=session['utils'], user=user)



@app.route('/users/add/', methods=["GET", "POST"])
@auth.login_required
def users_add():
    if request.method == "POST":
       addform =  [{'givenName': request.form['givenName'], 
                    'username' : request.form['sAMAccountName'], 
                    'password' : request.form['userPassword'],
                    'domain'   : request.form['domain']
                  }]
       model = UserModel(session['username'],session['password'])

       username = request.form['sAMAccountName']
       password = request.form['userPassword']
       mail = request.form['sAMAccountName'] + request.form['domain']
       fullname = "%s %s" %(request.form['givenName'], request.form['surname'])
       description = "SMB4Manager Created User"

       rid = model.AddUser(username)
       if (rid):
           user = User(username,fullname,description,rid);
           user.must_change_password = False
           user.password_never_expires = True
           model.UpdateUser(user)
           model.SetPassword(username, password)
           addform[0]['rid'] = rid
           addform[0]['description'] = description
           addform[0]['mail'] = mail
           alert_js = '<script type="text/javascript">alert("Username: %s Fullname: %s Created"); window.location="/users/";</script>' %(username, fullname)
           return alert_js

       return jsonify( { 'addform': addform[0] } )
    return render_template('users_add.html', utils=session['utils'])


@app.route('/users/del/<username>')
@auth.login_required
def users_del(username):
    if(username in session['username']): return redirect(url_for('users'))
    model = UserModel(session['username'],session['password'])
    del_user = model.DeleteUser(username)
    alert_js = '<script type="text/javascript">alert("Username: %s Deleted"); window.location="/users/";</script>' %(username)
    if (del_user): return alert_js
    return jsonify( { 'username': username } )



