from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
import os

from contextlib import asynccontextmanager

from config.database import ping_database
from config.database import client


from routes.route_routes import router as route_router
from routes.truck_routes import router as truck_router
from routes.trailer_routes import router as trailer_router
from routes.homebase_routes import router as homebase_router
from routes.typedowntime_routes import router as typedowntime_router
from routes.material_routes import router as material_router
from routes.destination_routes import router as destination_router
from routes.source_routes import router as source_router
from routes.operator_routes import router as operator_router
from routes.driver_routes import router as driver_router
from routes.landfill_routes import router as landfill_router

from routes.coversheet_routes import router as coversheet_router
from routes.sparetruckinfo_routes import router as sparetruckinfo_router
from routes.downtime_routes import router as downtime_router
from routes.load_routes import router as load_router

from routes.user_routes import router as user_router
from routes.email_routes import router as email_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    await ping_database()
    yield
    

app = FastAPI(lifespan=lifespan)

# Incluimos los orígenes permitidos en la configuración de CORS
# Si quiere permitir todos los orígenes, puedes usar unicamente ["*"]
origins = [
    "https://coversheet-app.onrender.com",
    "https://airc-coversheet.onrender.com",
    "http://www.render.com",
    "https://www.acedisposal.com",
    "https://airccoversheet.kizunadata.cloud"
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3500",  # <--- AGREGA ESTE (El que sale en tu error)
    "http://127.0.0.1:3500",  # <--- AGREGA ESTE por seguridad
    "http://[::1]:5173",      # <--- IPv6 de Windows para el frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    print("Hola desde el middleware")
    return response

# Sirve archivos estáticos desde la carpeta 'uploads'
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Incluijmos las rutas de la API

app.include_router(email_router, prefix="/api/utils", tags=["Email"])


app.include_router(route_router, prefix="/api/routes", tags=["Routes"])
app.include_router(truck_router, prefix="/api/trucks", tags=["Trucks"])
app.include_router(trailer_router, prefix="/api/trailers", tags=["Trailers"])
app.include_router(homebase_router, prefix="/api/homebases", tags=["Homebases"])
app.include_router(typedowntime_router, prefix="/api/typedowntimes", tags=["TypeDowntimes"])
app.include_router(material_router, prefix="/api/materials", tags=["Materiales"])
app.include_router(source_router, prefix="/api/sources", tags=["Sources"])
app.include_router(destination_router, prefix="/api/destinations", tags=["Destination"])
app.include_router(operator_router, prefix="/api/operators", tags=["Operators"])
app.include_router(driver_router, prefix="/api/drivers", tags=["Drivers"])
app.include_router(landfill_router, prefix="/api/landfills", tags=["Landfills"])

app.include_router(coversheet_router, prefix="/api/coversheets", tags=["Coversheets"])
app.include_router(sparetruckinfo_router, prefix="/api/sparetruckinfo", tags=["SpareTruckInfo"])
app.include_router(downtime_router, prefix="/api/downtime", tags=["Downtime"])
app.include_router(load_router, prefix="/api/load", tags=["Load"])

app.include_router(user_router, prefix="/api/users", tags=["Users"])



@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with MongoDB and Motor!"}