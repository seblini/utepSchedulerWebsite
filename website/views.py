from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import re
from .questionable_code import getFinal, toTable

views = Blueprint('views', __name__)

courses = ['MATH', 'SCI', 'CS', 'PHYS', 'EE']

def find(L, target):
    start = 0
    end = len(L) - 1

    while start <= end:
        middle = int((start + end)/ 2)
        midpoint = L[middle]
        if midpoint > target:
            end = middle - 1
        elif midpoint < target:
            start = middle + 1
        else:
            return True
    return False

@views.route('/schedule', methods=['GET', 'POST'])
@login_required
def generateSchedule():
    print('Generating Schedule...')
    gm = getFinal()
    toTable(gm)
    return render_template('schedule.html',  user=current_user)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('data')
        repeat = False

        for note2 in current_user.notes:
            if note == note2.data:
                repeat = True

        if repeat:
            flash('Course already added', category='error')
        elif not re.fullmatch(r'[A-Z]{2,4}\s\d{4}', note):
            flash('Invalid format', category='error')
        elif re.search(r'[A-Z]{2,4}', note).group() not in courses:
            flash('This course does not exist', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id,)
            db.session.add(new_note)
            db.session.commit()
            flash('Course added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})