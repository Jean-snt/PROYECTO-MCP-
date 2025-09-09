import os
import sys
import django


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reflexo.settings')
django.setup()

from inventory.models import Item, Order, OrderLine
from django.db import connection

def test_database_connection():
    print("=== Prueba de Conexión a Base de Datos MySQL ===")
    
    try:
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            print(f"✅ Conectado exitosamente a la base de datos: {db_name}")
        
        
        print(f"✅ Modelo Item: {Item.objects.count()} registros")
        print(f"✅ Modelo Order: {Order.objects.count()} registros")
        print(f"✅ Modelo OrderLine: {OrderLine.objects.count()} registros")
        
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [table[0] for table in cursor.fetchall()]
            print(f"✅ Tablas en la base de datos: {len(tables)}")
            
            
            inventory_tables = [t for t in tables if 'inventory' in t]
            print(f"✅ Tablas de inventory: {inventory_tables}")
        
        print("\n🎉 ¡La conexión a MySQL está funcionando perfectamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en la conexión: {str(e)}")
        return False

if __name__ == '__main__':
    test_database_connection()