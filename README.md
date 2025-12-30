Para correr el proyecto


Si es primera vez hay que preparar el ambiente virtual

pipx install virtualenv
pipx ensurepath
virtualenv entorno
source entorno/bin/activate
pip install --upgrade pip
pip install "fastapi[standard]"
pip install -r requirements.txt

Luego solo nos aseguramos que seleccionamos el interpretador correcto, (SHIFT + CTRL + P) o en mac (SHIFT + COMMAND + P)

______________________________________________
Ya una vez teniendo el poyecto configurado solo lo corremos uno de estos dos comandos, el segundo activa la funcion hot reload
uvicorn main:app --port 3500
uvicorn main:app --reload --port 3500


___________________________________________________________________________________________

Ejemplos de pprueba de paginacion de coversheet para postman :

🧪 Cómo Probar la Paginación en Postman
1️⃣ Navegación de Páginas

Página 1 (primera página - ya la tienes)
GET http://localhost:5173/api/coversheets/
✅ Resultado: Registros 1-50
Página 2
GET http://localhost:5173/api/coversheets/?page=2
✅ Resultado: Registros 51-100
Página 3
GET http://localhost:5173/api/coversheets/?page=3
✅ Resultado: Registros 101-150
Última página (306)
GET http://localhost:5173/api/coversheets/?page=306
✅ Resultado: Los últimos registros (debería tener has_next: false)

2️⃣ Cambiar Cantidad de Registros por Página

100 registros por página
GET http://localhost:5173/api/coversheets/?limit=100
✅ Resultado: 100 registros, total_pages cambia a 153
25 registros por página
GET http://localhost:5173/api/coversheets/?limit=25
✅ Resultado: 25 registros, total_pages cambia a 612
Combinar página + límite
GET http://localhost:5173/api/coversheets/?page=5&limit=100
✅ Resultado: Registros 401-500

3️⃣ Filtrar por Fecha

Solo registros del 28 de diciembre 2025
GET http://localhost:5173/api/coversheets/?start_date=2025-12-28&end_date=2025-12-28
✅ Resultado: Solo los 3 registros de esa fecha (según tu respuesta)
Registros de octubre 2025
GET http://localhost:5173/api/coversheets/?start_date=2025-10-01&end_date=2025-10-31
Registros desde octubre 2025 hasta ahora
GET http://localhost:5173/api/coversheets/?start_date=2025-10-01
Registros hasta octubre 2025
GET http://localhost:5173/api/coversheets/?end_date=2025-10-31

4️⃣ Filtrar por Camión/Driver/Trailer

Basándome en tu respuesta, veo estos IDs:
Filtrar por camión específico (ejemplo: Truck 725)
GET http://localhost:5173/api/coversheets/?truck_id=68f9c2673197bf6aed3d3fef
Filtrar por conductor específico (ejemplo: Angel Martinez Lopez)
GET http://localhost:5173/api/coversheets/?driver_id=6924eb35db1ca433b889758f
Filtrar por trailer específico (ejemplo: Trailer 918)
GET http://localhost:5173/api/coversheets/?trailer_id=68f9bfde3197bf6aed3d3fc3
Filtrar por homebase (ejemplo: IRL)
GET http://localhost:5173/api/coversheets/?homebase_id=68fbf9d3a696c170eef6148d

5️⃣ Combinar Múltiples Filtros

Camión 725 en diciembre 2025
GET http://localhost:5173/api/coversheets/?truck_id=68f9c2673197bf6aed3d3fef&start_date=2025-12-01&end_date=2025-12-31
Conductor Angel Martinez + Página 2 + 100 registros
GET http://localhost:5173/api/coversheets/?driver_id=6924eb35db1ca433b889758f&page=2&limit=100
Homebase IRL + Octubre 2025 + Ordenado por clockIn
GET http://localhost:5173/api/coversheets/?homebase_id=68fbf9d3a696c170eef6148d&start_date=2025-10-01&end_date=2025-10-31&sort_by=clockIn&sort_order=-1

6️⃣ Cambiar Ordenamiento

Ordenar por fecha ascendente (más antiguo primero)
GET http://localhost:5173/api/coversheets/?sort_order=1
Ordenar por clockIn descendente
GET http://localhost:5173/api/coversheets/?sort_by=clockIn&sort_order=-1
Ordenar por truckNumber ascendente
GET http://localhost:5173/api/coversheets/?sort_by=truckNumber&sort_order=1

7 Ejemplos con Rangos de Fechas

📅 Todo Diciembre 2025
GET http://localhost:5173/api/coversheets/?start_date=2025-12-01&end_date=2025-12-31
📅 Todo Octubre 2025
GET http://localhost:5173/api/coversheets/?start_date=2025-10-01&end_date=2025-10-31
📅 Un día específico (28 dic 2025)
GET http://localhost:5173/api/coversheets/?start_date=2025-12-28&end_date=2025-12-28
📅 Última semana de Octubre 2025
GET http://localhost:5173/api/coversheets/?start_date=2025-10-24&end_date=2025-10-31
📅 Todo el año 2025
GET http://localhost:5173/api/coversheets/?start_date=2025-01-01&end_date=2025-12-31
📅 Desde Octubre hasta ahora (solo start_date)
GET http://localhost:5173/api/coversheets/?start_date=2025-10-01
📅 Hasta Octubre (solo end_date)
GET http://localhost:5173/api/coversheets/?end_date=2025-10-31
📅 Trimestre Q4 2025 (Oct-Nov-Dec)
GET http://localhost:5173/api/coversheets/?start_date=2025-10-01&end_date=2025-12-31