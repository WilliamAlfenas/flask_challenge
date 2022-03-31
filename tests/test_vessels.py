import pytest
from flask_migrate import Migrate

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))

from apis.app import create_app
from apis.models.model import db
from apis.models.vessel import vessel
from sqlalchemy import func


@pytest.fixture(scope="module")
def app():
    app = create_app(test_config=True)
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        Migrate(app, db)

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_insert_clean_db(app):
    result = app.test_client().post('/vessel/insert_vessel', json={'code':'MV102'})
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201
    with app.app_context():
        query = db.session.query(vessel.code)
        query_results = db.session.execute(query).all()
        assert query_results[0][0] == 'MV102'

@pytest.mark.parametrize('description,input_data,expected_msg,expected_status', [
    (
        'test insert duplicated vessel code',
        {'code':'MV102'}, 
        'Duplicated vessel code', 
        409
    ),
    (
        'test insert without code',
        {}, 
        "{'code': ['Missing data for required field.']}", 
        400
    ),
    (
        'test insert an empty code',
        {'code':''}, 
        "{'code': ['Length must be between 1 and 8.']}", 
        400
    ),
    (
        'test insert over 8 characters code',
        {'code':'123456789'}, 
        "{'code': ['Length must be between 1 and 8.']}", 
        400
    )
])
def test_insert_invalid_inputs(app, description, input_data, expected_msg, expected_status):
    result = app.test_client().post('/vessel/insert_vessel', json=input_data)
    assert result.get_json().get('message') == expected_msg
    assert result.status_code == expected_status, description
    with app.app_context():
        query = db.session.query(func.count(vessel.code))
        query_results = db.session.execute(query).all()
        assert query_results[0][0] == 1, description

if __name__ == '__main__':
    pytest.main(['tests/test_vessels.py'])