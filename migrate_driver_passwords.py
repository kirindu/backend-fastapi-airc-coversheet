"""
Script para hashear contraseñas existentes de drivers
Ejecutar: python migrate_driver_passwords.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from bson import ObjectId
import os

# Configuración
MONGO_URL = "mongodb+srv://airc_db_admin:kGNM4HKhDmCwvjv5@clustertest.yatkudm.mongodb.net/"
DATABASE_NAME = "airc_coversheet_db_staging"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def migrate_passwords():
    # Conectar a MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    drivers_collection = db["drivers"]
    
    print("Iniciando migración de contraseñas...")
    print("=" * 60)
    
    # Buscar todos los drivers con contraseñas en texto plano
    # Las contraseñas hasheadas con bcrypt empiezan con "$2b$"
    cursor = drivers_collection.find({
        "password": {"$not": {"$regex": "^\\$2b\\$"}}
    })
    
    drivers = await cursor.to_list(length=None)
    total = len(drivers)
    
    if total == 0:
        print("✅ No hay contraseñas para migrar. Todas ya están hasheadas.")
        return
    
    print(f"Encontrados {total} drivers con contraseñas sin hashear")
    print()
    
    updated = 0
    errors = 0
    
    for driver in drivers:
        try:
            driver_id = driver["_id"]
            username = driver.get("username", "N/A")
            plain_password = driver.get("password", "")
            
            if not plain_password:
                print(f"⚠️  Driver {username} no tiene contraseña, saltando...")
                continue
            
            # Hashear la contraseña
            hashed_password = pwd_context.hash(plain_password)
            
            # Actualizar en la base de datos
            result = await drivers_collection.update_one(
                {"_id": driver_id},
                {"$set": {"password": hashed_password}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Actualizado: {username}")
                updated += 1
            else:
                print(f"⚠️  No se actualizó: {username}")
                
        except Exception as e:
            errors += 1
            print(f"❌ Error con driver {username}: {str(e)}")
    
    print()
    print("=" * 60)
    print("RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    print(f"Total de drivers:        {total}")
    print(f"Actualizados:            {updated}")
    print(f"Errores:                 {errors}")
    print("=" * 60)
    
    # Verificación
    print("\nVerificando migración...")
    remaining = await drivers_collection.count_documents({
        "password": {"$not": {"$regex": "^\\$2b\\$"}}
    })
    
    if remaining == 0:
        print("✅ Migración completada exitosamente!")
    else:
        print(f"⚠️  Aún quedan {remaining} contraseñas sin hashear")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_passwords())