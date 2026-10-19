from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Resource

from backend.extensions import db
from backend.models import Note, User


def get_owned_note(note_id, user_id):
    """Look up a note and confirm the caller owns it.

    Returns (note, None) on success, or (None, error_response) so the caller
    can return the tuple straight through to Flask-RESTful.
    """
    note = db.session.get(Note, note_id)
    if note is None:
        return None, ({"error": "note not found"}, 404)
    if note.user_id != user_id:
        return None, ({"error": "not authorized to access this note"}, 403)
    return note, None


class SignupResource(Resource):
    def post(self):
        payload = request.get_json(silent=True) or {}
        username = payload.get('username')
        password = payload.get('password')

        if not username or not password:
            return {"error": "username and password are required"}, 400

        if User.query.filter_by(username=username).first():
            return {"error": "username already exists"}, 409

        try:
            user = User(username=username)
            user.password = password
            db.session.add(user)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 400

        return user.to_dict(), 201


class LoginResource(Resource):
    def post(self):
        payload = request.get_json(silent=True) or {}
        username = payload.get('username')
        password = payload.get('password')

        if not username or not password:
            return {"error": "username and password are required"}, 400

        user = User.query.filter_by(username=username).first()
        # One message for both failure modes, so the response does not reveal
        # which usernames exist.
        if not user or not user.check_password(password):
            return {"error": "invalid username or password"}, 401

        access_token = create_access_token(identity=str(user.id))
        return {"access_token": access_token, "user": user.to_dict()}, 200


class MeResource(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if user is None:
            return {"error": "user not found"}, 404

        return user.to_dict(), 200


class NotesListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=5, type=int)
        # Cap the page size so a client cannot request the whole table at once.
        per_page = min(per_page, 25)

        pagination = (
            Note.query.filter_by(user_id=user_id)
            .order_by(Note.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            "items": [note.to_dict() for note in pagination.items],
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        payload = request.get_json(silent=True) or {}
        title = payload.get('title')
        content = payload.get('content')

        if not title or not content:
            return {"error": "title and content are required"}, 400

        try:
            note = Note(title=title, content=content, user_id=user_id)
            db.session.add(note)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 400

        return note.to_dict(), 201


class NoteDetailResource(Resource):
    @jwt_required()
    def get(self, note_id):
        user_id = int(get_jwt_identity())
        note, error = get_owned_note(note_id, user_id)
        if error:
            return error

        return note.to_dict(), 200

    @jwt_required()
    def patch(self, note_id):
        user_id = int(get_jwt_identity())
        note, error = get_owned_note(note_id, user_id)
        if error:
            return error

        payload = request.get_json(silent=True) or {}
        title = payload.get('title')
        content = payload.get('content')

        # Only the fields present in the request body are touched.
        try:
            if title is not None:
                note.title = title
                note.validate_title()
            if content is not None:
                note.content = content
                note.validate_content()
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 400

        return note.to_dict(), 200

    @jwt_required()
    def delete(self, note_id):
        user_id = int(get_jwt_identity())
        note, error = get_owned_note(note_id, user_id)
        if error:
            return error

        db.session.delete(note)
        db.session.commit()
        return {"message": "note deleted successfully"}, 200
