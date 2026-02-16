from dataclasses import asdict

from sqlalchemy import select

from fast_pr.models import Users


def test_create_user(session, mock_db):
    with mock_db(model=Users) as time:
        new_user = Users(
            name='Bob', password='as34ty', email='bob@example.com'
        )
        # send info to db
        session.add(new_user)
        session.commit()

    user = session.scalar(select(Users).where(Users.name == 'Bob'))
    # get and show data from db

    assert asdict(user) == {
        'id': 1,
        'name': 'Bob',
        'password': 'as34ty',
        'email': 'bob@example.com',
        'creation': time,
        'last_update': time,
    }

    # --> verify structure in db
