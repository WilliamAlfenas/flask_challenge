import pytest
from flask_migrate import Migrate

import sys
import os

from apis.models.operation_order import OperationOrder
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))

from apis.app import create_app
from apis.models.model import db
from apis.models.vessel import vessel
from apis.models.equipment import equipment
from sqlalchemy import func


@pytest.fixture(scope="module")
def app():
    app = create_app(test_config=True)
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        Migrate(app, db)
        
        vessel_obj1 = vessel(code='MV102')
        vessel_obj2 = vessel(code='MV101')

        equip_ob1 = equipment(
            **{'vessel_id':1, 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'}
        )
        equip_ob2 = equipment(
            **{'vessel_id':2, 'code':'5310B9D8', 'location':'brazil', 'name':'compressor'}
        )
        
        db.session.add(vessel_obj1)
        db.session.add(vessel_obj2)
        db.session.commit()
        db.session.add(equip_ob1)
        db.session.add(equip_ob2)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_insert_clean_db(app):
    result = app.test_client().post(
        '/operation_order/insert_operation', 
        json={'code':'5310B9D7', 'type': 'replacement', 'cost': 123.45}
    )
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201

    result = app.test_client().post(
        '/operation_order/insert_operation', 
        json={'code':'5310B9D8', 'type': 'instalation', 'cost': 234.56}
    )
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201

    with app.app_context():
        query = db.session.query(OperationOrder)\
            .order_by(OperationOrder.id)
        query_results = db.session.execute(query).all()
        assert query_results[0][0].id == 1
        assert query_results[0][0].equipment_id == 1
        assert query_results[0][0].type == 'replacement'
        assert query_results[0][0].cost == 123.45
        assert query_results[1][0].id == 2
        assert query_results[1][0].equipment_id == 2
        assert query_results[1][0].type == 'instalation'
        assert query_results[1][0].cost == 234.56

@pytest.mark.parametrize(
    'description,endpoint,method,'\
    'input_data,expected_resp,expected_status', [
    (
        'test insert invalid equipment code',
        '/operation_order/insert_operation', 'post',
        {'code':'INVALID', 'type': 'replacement', 'cost': 123.45}, 
        {'message': 'Invalid equipment code'}, 
        400
    ),
    (
        'test total_cost by code 5310B9D8',
        '/operation_order/total_cost', 'get',
        {'code':'5310B9D8'}, 
        {'total_cost': 234.56}, 
        200
    ),
    (
        'test total_cost by name compressor',
        '/operation_order/total_cost', 'get',
        {'name':'compressor'}, 
        {'total_cost': 234.56+123.45}, 
        200
    ),
    (
        'test total_cost with invalid code',
        '/operation_order/total_cost', 'get',
        {'code':'INVALID'}, 
        {'message': 'Invalid parameters'}, 
        400
    ),
    (
        'test average_cost',
        '/operation_order/average_cost', 'get',
        {}, 
        {'MV101': 234.56, 'MV102': 123.45},
        200
    )
])
def test_operation_cases(
    app, description, 
    endpoint, method, input_data, 
    expected_resp, expected_status
):
    client = app.test_client()
    request_handler = client.get \
        if method == 'get' else client.post
    result = request_handler(
        endpoint, json=input_data
    ) 

    assert result.get_json() == expected_resp
    assert result.status_code == expected_status, description
    with app.app_context():
        query = db.session.query(func.count(OperationOrder.id))
        query_results = db.session.execute(query).all()
        assert query_results[0][0] == 2, description

if __name__ == '__main__':
    pytest.main(['tests/test_operations.py'])