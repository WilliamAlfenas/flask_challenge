import pytest
from flask_migrate import Migrate

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))

from apis.app import create_app
from apis.models.model import db
from apis.models.vessel import vessel
from apis.models.equipment import equipment
from sqlalchemy import func, or_


@pytest.fixture(scope="module")
def app():
    app = create_app(test_config=True)
    
    with app.app_context():
        db.create_all()
        Migrate(app, db)
        vessel_obj1 = vessel(code='MV102')
        vessel_obj2 = vessel(code='MV101')
        db.session.add(vessel_obj1)
        db.session.add(vessel_obj2)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_insert_clean_db(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'})
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1
        assert query_results[0][0].vessel_id == 1
        assert query_results[0][0].code == '5310B9D7'
        assert query_results[0][0].location == 'brazil'
        assert query_results[0][0].active
        assert query_results[0][0].name == 'compressor'

def test_insert_without_vessel_code(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'code':'5310B9D7', 'location':'brazil', 'name':'compressor'})
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_without_code(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'location':'brazil', 'name':'compressor'})
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_without_location(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'code':'5310B9D7', 'name':'compressor'})
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_without_name(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'code':'5310B9D7', 'location':'brazil'})
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1
