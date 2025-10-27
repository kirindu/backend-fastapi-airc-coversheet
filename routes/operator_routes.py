from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.operator_model import OperatorModel
from config.database import operators_collection
from schemas.operator_scheme import operator_helper
from bson import ObjectId

router = APIRouter()

 
@router.post("/")
async def create_operator(operator: OperatorModel):
    try:
        new = await operators_collection.insert_one(operator.model_dump())
        created = await operators_collection.find_one({"_id": new.inserted_id})
        return success_response(operator_helper(created), msg="Operators creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el operator: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_operators():
    try:
        operators = [operator_helper(operator) async for operator in operators_collection.find().sort("operatorName", 1)]
        return success_response(operators, msg="Lista de operators obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los operators: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_operator(id: str):
    operator = await operators_collection.find_one({"_id": ObjectId(id)})
    if operator:
        return success_response(operator_helper(operator), msg="Operator encontrado")
    return error_response("Operator no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_operator(id: str, operator: OperatorModel):
    res = await operators_collection.update_one({"_id": ObjectId(id)}, {"$set": operator.model_dump()})
    if res.matched_count == 0:
        return error_response("Operator no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await operators_collection.find_one({"_id": ObjectId(id)})
    return success_response(operator_helper(updated), msg="Operator actualizado")

@router.delete("/{id}")
async def delete_operator(id: str):
    res = await operators_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return success_response(None, msg="Operator eliminado")
    return error_response("Operator no encontrado", status_code=status.HTTP_404_NOT_FOUND)    