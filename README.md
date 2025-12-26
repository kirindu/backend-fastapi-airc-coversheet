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
