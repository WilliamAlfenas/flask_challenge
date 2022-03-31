import logging
from flask import Blueprint, request
from psycopg2.errors import UniqueViolation
from sqlalchemy import func, or_

from apis.models.equipment import equipment
from apis.models.operation_order import OperationOrder
from apis.models.vessel import vessel
from apis.models.model import db
import apis.models.schemas as schemas 


logging.basicConfig(format='%(levelname)s - %(asctime)s (%(filename)s:%(funcName)s): %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

healthcheck_blueprint = Blueprint('healthcheck', __name__)
vessels_blueprint = Blueprint('vessels', __name__)
equipments_blueprint = Blueprint('equipments', __name__)
operation_order_blueprint = Blueprint('operation_order', __name__)

create_vessel_schema = schemas.CreateVesselInputSchema()
create_equipment_schema = schemas.CreateEquipmentInputSchema()
update_equipment_schema = schemas.UpdateEquipmentInputSchema()
active_equipment_schema = schemas.ActiveEquipmentInputSchema()
equipments_output_schema = schemas.EquipmentOutputSchema(many=True)
create_operation_schema = schemas.CreateOperationOrderInputSchema()
total_cost_schema = schemas.TotalCostOperationInputSchema()

@healthcheck_blueprint.route('/', methods=['GET'])
def healthcheck():

    """Checks if the system is alive
        ---
        responses:
          200:
            description: OK if the system is alive
    """
    logging.basicConfig(format='%(levelname)s - %(asctime)s (%(filename)s:%(funcName)s): %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('Test the health of the system')
    return 'OK', 200


@vessels_blueprint.route('/insert_vessel', methods=['POST'])
def insert_vessel():
    """Insert a new vessel
        ---
        parameters:
            - name: code
              in: body
              type: string
              required: true
        responses:
          201:
            description: OK
          400:
            description: Error description
          409:
            description: Duplicated vessel code
    """
    input_data = request.json
    errors = create_vessel_schema.validate(input_data)
    if errors:
      return {'message':str(errors)}, 400

    new_vessel = vessel(code = input_data.get('code'))

    message, status_code = 'OK', 201
    transaction = db.session
    try:
      transaction.add(new_vessel)
      transaction.commit()
    except Exception as e:
      transaction.rollback()
      if isinstance(e.orig, UniqueViolation):
        message, status_code = 'Duplicated vessel code', 409
      else:
        logger.error(e)
        message, status_code = str(e), 400

    return {'message':message}, status_code

@equipments_blueprint.route('/insert_equipment', methods=['POST'])
def insert_equipment():
    """insert_equipment
        ---
        parameters:
            - name: vessel_code
              in: body
              type: string
              required: true
            - name: code
              in: body
              type: string
              required: true
            - name: name
              in: body
              type: string
              required: true
            - name: location
              in: body
              type: string
              required: true
        responses:
          201:
            description: returns OK if the equipment was correctly inserted
          400:
            description: Error
    """
    input_data = request.json
    errors = create_equipment_schema.validate(input_data)
    if errors:
      return {'message':str(errors)}, 400
    
    ref_vessel = db.session.query(vessel).filter(
      vessel.code == input_data.get('vessel_code')
    ).first()

    if not ref_vessel:
      return {'message': 'Invalid vessel code'}, 400
    
    new_equipment = equipment(
      vessel_id=ref_vessel.id,
      name=input_data.get('name'),
      code=input_data.get('code'),
      location=input_data.get('location'),
      active=True
    )

    message, status_code = 'OK', 201
    transaction = db.session
    try:
      transaction.add(new_equipment)
      transaction.commit()
    except Exception as e:
      transaction.rollback()
      if isinstance(e.orig, UniqueViolation):
        message, status_code = 'Duplicated equipment code', 409
      else:
        logger.error(e)
        message, status_code = str(e), 400

    return {'message':message}, status_code

@equipments_blueprint.route('/update_equipment_status', methods=['PUT'])
def update_equipment_status():
    """update_equipment_status
        ---
        parameters:
            - name: codes
              in: body
              type: list of string
              required: true
        responses:
          201:
            description: returns OK if the equipments were correctly updated
          400:
            description: Error
    """
    input_data = request.json
    errors = update_equipment_schema.validate(input_data)
    if errors:
      return {'message':str(errors)}, 400

    message, status_code = 'OK', 201
    transaction = db.session
    try:
      transaction.query(equipment).filter(
        equipment.code.in_(
          input_data.get('codes')
        )
      ).update({
        equipment.active: False
      })
      transaction.commit()
    except Exception as e:
      transaction.rollback()
      if isinstance(e.orig, UniqueViolation):
        message, status_code = 'Duplicated equipment code', 409
      else:
        logger.error(e)
        message, status_code = str(e), 400

    return {'message':message}, status_code

@equipments_blueprint.route('/active_equipments', methods=['GET'])
def active_equipment():
    """active_equipments
        ---
        parameters:
            - name: vessel_code
              in: query
              type: string
              required: true
        responses:
          200:
            description: returns a json with equipments key and a list of equipments
          400:
            description: error
    """
    input_data = request.json
    errors = active_equipment_schema.validate(input_data)
    if errors:
      return {'message':str(errors)}, 400

    ref_vessel = db.session.query(vessel).filter(
      vessel.code == input_data.get('vessel_code')
    ).first()

    if not ref_vessel:
      return {'message': 'Invalid vessel code'}, 400

    try:
      equipments = db.session.query(equipment).filter(
        equipment.vessel_id == ref_vessel.id \
          and equipment.active == True
      ).all()
    except Exception as e:
      logger.error(e)
      return {'message': str(e)}, 400

    return {
      ref_vessel.code: equipments_output_schema.dump(equipments)
    }, 200

@operation_order_blueprint.route('/insert_operation', methods=['POST'])
def insert_operation():
    """insert_operation
        ---
        parameters:
            - name: equipment_code
              in: body
              type: string
              required: true
            - name: type
              in: body
              type: string
              required: true
            - name: cost
              in: body
              type: float
              required: true
        responses:
          201:
            description: returns OK if the equipment was correctly inserted
          400:
            description: Error
    """
    input_data = request.json
    errors = create_operation_schema.validate(input_data)
    if errors:
      return {'message':str(errors)}, 400
    
    ref_equipment = db.session.query(equipment).filter(
      equipment.code == input_data.get('code')
    ).first()

    if not ref_equipment:
      return {'message': 'Invalid equipment code'}, 400
    
    new_operation = OperationOrder(
      equipment_id = ref_equipment.id,
      type=input_data.get('type'),
      cost=input_data.get('cost')
    )

    message, status_code = 'OK', 201
    transaction = db.session
    try:
      transaction.add(new_operation)
      transaction.commit()
    except Exception as e:
      transaction.rollback()
      logger.error(e)
      message, status_code = str(e), 400

    return {'message':message}, status_code

@operation_order_blueprint.route('/total_cost', methods=['GET'])
def total_cost():
    """total_cost
        ---
        parameters:
            - name: code
              in: query
              type: string
              required: false
            - name: name
              in: query
              type: string
              required: false
        responses:
          200:
            description: returns a json with equipments key and a list of equipments
          400:
            description: error
    """
    input_data = request.json
    errors = total_cost_schema.validate(input_data)
    if errors:
      return {'message':str(errors)}, 400

    ref_equipments = db.session.query(equipment).filter(
      or_(
        equipment.code == input_data.get('code', ''),
        equipment.name == input_data.get('name', '')
      )
    ).all()

    if len(ref_equipments) < 1:
      return {'message': 'Invalid parameters'}, 400

    total = .0
    try:
      total = db.session.query(
        func.sum(OperationOrder.cost).label('total')
      ).filter(
        OperationOrder.equipment_id.in_([
          equip.id
          for equip in ref_equipments
        ])
      ).first()[0]

    except Exception as e:
      logger.error(e)
      return {'message': str(e)}, 400

    return {
      'total_cost': total
    }, 200

@operation_order_blueprint.route('/average_cost', methods=['GET'])
def average_cost():
    """average_cost
        ---
        responses:
          200:
            description: returns a json with equipments key and a list of equipments
          400:
            description: error
    """

    try:
      averages = db.session.query(
        func.avg(OperationOrder.cost).label('average'),
        vessel.code
      ).join(
        equipment, equipment.id == OperationOrder.equipment_id
      ).join(
        vessel, vessel.id == equipment.vessel_id
      ).group_by(
        vessel.code
      ).all()
    except Exception as e:
      logger.error(e)
      return {'message': str(e)}, 400

    return {
      row.code: round(row.average, 2)
      for row in averages
    }, 200