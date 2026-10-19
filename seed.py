#!/usr/bin/env python3

from faker import Faker

from app import create_app
from backend.extensions import db
from backend.models import Note, User

fake = Faker()
app = create_app()

with app.app_context():
    print("Clearing tables...")
    db.drop_all()
    db.create_all()

    print("Seeding users...")
    alice = User(username='alice')
    alice.password = 'password123'
    bob = User(username='bob')
    bob.password = 'password123'

    db.session.add_all([alice, bob])
    db.session.commit()

    print("Seeding notes...")
    # Alice gets more than one page of notes so pagination is easy to test.
    notes = []
    for _ in range(12):
        notes.append(
            Note(
                title=fake.sentence(nb_words=4),
                content=fake.paragraph(nb_sentences=3),
                user_id=alice.id,
            )
        )

    for _ in range(6):
        notes.append(
            Note(
                title=fake.sentence(nb_words=4),
                content=fake.paragraph(nb_sentences=3),
                user_id=bob.id,
            )
        )

    db.session.add_all(notes)
    db.session.commit()

    print("Done seeding.")
