#!/bin/zsh
# TALENTO SOSTENIBLE - CRM
# Doble clic para arrancar

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

source venv/bin/activate

# Arranca el servidor
python manage.py runserver &
SERVER_PID=$!

# Espera a que el servidor este listo
sleep 2

# Abre el navegador
open http://127.0.0.1:8000/

echo ""
echo "=========================================="
echo "  TALENTO SOSTENIBLE esta corriendo"
echo "  http://127.0.0.1:8000/"
echo ""
echo "  Para cerrar: pulsa Control+C"
echo "=========================================="
echo ""

# Espera a que el usuario cierre con Control+C
trap "kill $SERVER_PID 2>/dev/null; exit" INT TERM
wait $SERVER_PID
