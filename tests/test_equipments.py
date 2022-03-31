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
        db.drop_all()
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
    result = app.test_client().post(
        '/equipment/insert_equipment', 
        json={'vessel_code':'MV102', 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'}
    )
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

@pytest.mark.parametrize('description,input_data,expected_msg,expected_status', [
    (   
        'test insert without vessel code',    
        {'code':'5310B9D7', 'location':'brazil', 'name':'compressor'}, 
        "{'vessel_code': ['Missing data for required field.']}", 
        400
    ),(   
        'test insert empty vessel code',    
        {'vessel_code':'', 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'}, 
        "{'vessel_code': ['Length must be between 1 and 8.']}", 
        400
    ),
    (   
        'test insert invalid vessel code',    
        {'vessel_code':'INVALID', 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'}, 
        "Invalid vessel code", 
        400
    ),
    (   
        'test insert without code',    
        {'vessel_code':'MV102', 'location':'brazil', 'name':'compressor'}, 
        "{'code': ['Missing data for required field.']}", 
        400
    ),
    (   
        'test insert empty code',    
        {'vessel_code':'MV102', 'code':'', 'location':'brazil', 'name':'compressor'}, 
        "{'code': ['Length must be between 1 and 8.']}", 
        400
    ),
    (   
        'test insert duplicated code',    
        {'vessel_code':'MV102', 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'}, 
        "Duplicated equipment code", 
        409
    ),
    (   
        'test insert without location',    
        {'vessel_code':'MV102', 'code':'5310B9D7', 'name':'compressor'}, 
        "{'location': ['Missing data for required field.']}", 
        400
    ),
    (   
        'test insert empty location',    
        {'vessel_code':'MV102', 'code':'5310B9D7', 'location':'', 'name':'compressor'}, 
        "{'location': ['Length must be between 1 and 256.']}", 
        400
    ),
    (   
        'test insert without name',    
        {'vessel_code':'MV102', 'code':'5310B9D7', 'location':'brazil'}, 
        "{'name': ['Missing data for required field.']}", 
        400
    ),
    (   
        'test insert empty name',    
        {'vessel_code':'MV102', 'code':'5310B9D7', 'location':'brazil', 'name':''}, 
        "{'name': ['Length must be between 1 and 256.']}", 
        400
    )
])
def test_insert_invalid_inputs(app, description, input_data, expected_msg, expected_status):
    result = app.test_client().post('/equipment/insert_equipment', json=input_data)
    assert result.get_json().get('message') == expected_msg
    assert result.status_code == expected_status, description
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1, description


def test_insert_more_equipment(app):
    result = app.test_client().post(
        '/equipment/insert_equipment', 
        json={'vessel_code':'MV101', 'code':'5310B9D8', 'location':'brazil', 'name':'compressor'}
    )
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 2
        assert query_results[1][0].vessel_id == 2
        assert query_results[1][0].code == '5310B9D8'
        assert query_results[1][0].location == 'brazil'
        assert query_results[1][0].active
        assert query_results[1][0].name == 'compressor'

@pytest.mark.parametrize('description,input_data,expected_resp,expected_status', [
    (   
        'test get actives equipment from MV102',    
        {'vessel_code':'MV102'}, 
        {'MV102': [{'code': '5310B9D7', 'id': 1, 'location': 'brazil', 'name': 'compressor', 'vessel_id': 1}]}, 
        200
    ),
    (   
        'test get actives equipment from MV101',    
        {'vessel_code':'MV101'}, 
        {'MV101': [{'code': '5310B9D8', 'id': 3, 'location': 'brazil', 'name': 'compressor', 'vessel_id': 2}]}, 
        200
    ),
    (   
        'test get actives equipment without vessel code',    
        {}, 
        {'message': "{'vessel_code': ['Missing data for required field.']}"},
        400
    ),
    (   
        'test get actives equipment with empty code',    
        {'vessel_code':''}, 
        {'message': "{'vessel_code': ['Length must be between 1 and 8.']}"},
        400
    ),
    (   
        'test get actives equipment with invalid vessel code',    
        {'vessel_code':'INVALID'}, 
        {'message': 'Invalid vessel code'},
        400
    )
])
def test_get_active_cases(app, description, input_data, expected_resp, expected_status):
    result = app.test_client().get('/equipment/active_equipments', json=input_data)
    assert result.get_json() == expected_resp
    assert result.status_code == expected_status, description
    with app.app_context():
        query = db.session.query(equipment)\
            .order_by(equipment.vessel_id)
        query_results = db.session.execute(query).all()

        assert len(query_results) == 2, description

@pytest.mark.parametrize('description,input_data,expected_msg,expected_status', [
    (   
        'test update multiple codes',    
        {'codes':['5310B9D7', '5310B9D8']}, 
        "OK", 
        201
    ),
    (   
        'test update one code',    
        {'codes':['5310B9D7']}, 
        "OK", 
        201
    ),
    (   
        'test update without codes',    
        {}, 
        "{'codes': ['Missing data for required field.']}", 
        400
    ),
    (   
        'test update empty codes',    
        {'codes':['', '']}, 
        "{'codes': {0: ['Length must be between 1 and 8.'], 1: ['Length must be between 1 and 8.']}}",  
        400
    )
])
def test_update_cases(app, description, input_data, expected_msg, expected_status):
    result = app.test_client().put('/equipment/update_equipment_status', json=input_data)
    assert result.get_json().get('message') == expected_msg
    assert result.status_code == expected_status, description
    with app.app_context():
        query = db.session.query(equipment)\
            .order_by(equipment.vessel_id)
        query_results = db.session.execute(query).all()

        assert len(query_results) == 2, description
        assert query_results[0][0].vessel_id == 1, description
        assert query_results[0][0].code == '5310B9D7', description
        assert query_results[0][0].location == 'brazil', description
        assert query_results[0][0].active == False, description
        assert query_results[0][0].name == 'compressor', description

        assert query_results[1][0].vessel_id == 2, description
        assert query_results[1][0].code == '5310B9D8', description
        assert query_results[1][0].location == 'brazil', description
        assert query_results[1][0].active == False, description
        assert query_results[1][0].name == 'compressor', description

if __name__ == '__main__':
    pytest.main(['tests/test_equipments.py'])