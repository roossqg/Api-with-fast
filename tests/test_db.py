from sqlalchemy import select

from fast_pr.models import Users


def test_create_user(session):
    new_user = Users(name='Bob', password='as34ty', email='bob@example.com')
    # send info to db

    session.add(new_user)
    session.commit()

    user = session.scalar(select(Users).where(Users.name == 'Bob'))
    # get and show data from db

    assert user.name == 'Bob'
    # --> verify cond in db
