# Database Migrations - Sistema de Control de Versiones de Base de Datos

Este directorio contiene las migraciones de Django para la aplicación `inventory`, implementando un sistema robusto de control de versiones para la estructura de la base de datos. Las migraciones garantizan la evolución controlada y segura del esquema de datos del inventario médico.

## 🏗️ Arquitectura de Migraciones

Las migraciones de Django implementan un patrón de versionado incremental que permite:
- **Evolución controlada**: Cambios graduales y rastreables en el esquema
- **Reversibilidad**: Capacidad de deshacer cambios de forma segura
- **Sincronización**: Consistencia entre diferentes entornos de desarrollo
- **Integridad referencial**: Mantenimiento de relaciones entre tablas

## 📁 Estructura de Archivos de Migración

### `__init__.py` - Inicializador del Paquete
Archivo que define este directorio como un paquete Python válido, permitiendo la importación de módulos de migración.

### `0001_initial.py` - Migración Inicial
La migración fundacional que establece el esquema base de la aplicación:

#### Estructura de la Migración Inicial
```python
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=50, unique=True, verbose_name='SKU')),
                ('name', models.CharField(max_length=200, verbose_name='Nombre')),
                ('medicine_type', models.CharField(max_length=100, verbose_name='Tipo de Medicamento')),
                ('disease_category', models.CharField(max_length=100, verbose_name='Categoría de Enfermedad')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio')),
                ('stock', models.IntegerField(verbose_name='Stock')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
            ],
            options={
                'verbose_name': 'Medicamento',
                'verbose_name_plural': 'Medicamentos',
                'ordering': ['name'],
            },
        ),
    ]
```

#### Características de la Migración Inicial
- **Modelo Item**: Estructura completa para medicamentos
- **Campos optimizados**: Tipos de datos apropiados para cada campo
- **Restricciones de integridad**: SKU único, campos requeridos
- **Metadatos**: Configuración de ordenamiento y nombres verbosos
- **Timestamps automáticos**: Seguimiento de creación y modificación

### Migraciones Subsecuentes (Patrón de Numeración)
Cada migración posterior sigue el patrón `XXXX_descriptive_name.py`:
- **0002_add_indexes.py**: Adición de índices para optimización
- **0003_add_category_field.py**: Nuevos campos de categorización
- **0004_modify_price_precision.py**: Ajustes en precisión de precios

## 🔄 Ciclo de Vida de las Migraciones

### 1. Detección de Cambios
```bash
# Django detecta cambios en models.py
python manage.py makemigrations inventory
```

### 2. Generación de Migración
```python
# Django genera automáticamente el archivo de migración
class Migration(migrations.Migration):
    dependencies = [('inventory', '0001_initial')]
    
    operations = [
        migrations.AddField(
            model_name='item',
            name='new_field',
            field=models.CharField(max_length=100, default=''),
        ),
    ]
```

### 3. Aplicación de Migración
```bash
# Aplicar migraciones pendientes
python manage.py migrate inventory
```

### 4. Verificación de Estado
```bash
# Verificar estado de migraciones
python manage.py showmigrations inventory
```

## 🛠️ Comandos de Gestión de Migraciones

### Comandos Básicos
```bash
# Crear nuevas migraciones basadas en cambios en models.py
python manage.py makemigrations inventory

# Aplicar todas las migraciones pendientes
python manage.py migrate inventory

# Aplicar migración específica
python manage.py migrate inventory 0001

# Ver estado de todas las migraciones
python manage.py showmigrations

# Ver estado específico de inventory
python manage.py showmigrations inventory
```

### Comandos Avanzados
```bash
# Crear migración vacía para operaciones personalizadas
python manage.py makemigrations --empty inventory

# Ver SQL que se ejecutará sin aplicar cambios
python manage.py sqlmigrate inventory 0001

# Revertir a migración específica
python manage.py migrate inventory 0001

# Marcar migración como aplicada sin ejecutar
python manage.py migrate --fake inventory 0001

# Deshacer todas las migraciones de inventory
python manage.py migrate inventory zero
```

## 🔍 Tipos de Operaciones de Migración

### Operaciones de Esquema
```python
# Crear modelo
migrations.CreateModel(name='NewModel', fields=[...])

# Eliminar modelo
migrations.DeleteModel(name='OldModel')

# Agregar campo
migrations.AddField(model_name='item', name='new_field', field=...)

# Eliminar campo
migrations.RemoveField(model_name='item', name='old_field')

# Modificar campo
migrations.AlterField(model_name='item', name='field', field=...)

# Renombrar campo
migrations.RenameField(model_name='item', old_name='old', new_name='new')
```

### Operaciones de Datos
```python
# Migración de datos personalizada
def migrate_data(apps, schema_editor):
    Item = apps.get_model('inventory', 'Item')
    for item in Item.objects.all():
        # Lógica de migración de datos
        item.new_field = transform_data(item.old_field)
        item.save()

# Operación de migración de datos
migrations.RunPython(migrate_data, reverse_migrate_data)
```

### Operaciones de Índices
```python
# Agregar índice
migrations.AddIndex(
    model_name='item',
    index=models.Index(fields=['sku', 'name'], name='item_sku_name_idx')
)

# Eliminar índice
migrations.RemoveIndex(model_name='item', name='item_sku_name_idx')
```

## 📊 Monitoreo y Auditoría de Migraciones

### Tabla de Estado de Migraciones
Django mantiene una tabla `django_migrations` que registra:
- **ID**: Identificador único de la migración
- **App**: Aplicación a la que pertenece
- **Name**: Nombre del archivo de migración
- **Applied**: Timestamp de aplicación

### Consulta de Estado
```sql
-- Ver todas las migraciones aplicadas
SELECT * FROM django_migrations WHERE app = 'inventory';

-- Ver última migración aplicada
SELECT * FROM django_migrations 
WHERE app = 'inventory' 
ORDER BY applied DESC 
LIMIT 1;
```

## 🚨 Mejores Prácticas y Consideraciones

### Desarrollo Seguro
- **Backup antes de migrar**: Siempre respaldar datos en producción
- **Pruebas en desarrollo**: Validar migraciones en entorno de desarrollo
- **Migraciones atómicas**: Usar transacciones para operaciones complejas
- **Reversibilidad**: Implementar operaciones de reversa cuando sea posible

### Optimización de Rendimiento
```python
# Migración optimizada para grandes volúmenes de datos
class Migration(migrations.Migration):
    atomic = False  # Desactivar transacciones automáticas
    
    operations = [
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY idx_item_sku ON inventory_item(sku);",
            reverse_sql="DROP INDEX idx_item_sku;"
        ),
    ]
```

### Gestión de Dependencias
```python
class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),  # Dependencia externa
    ]
```

## 🔧 Resolución de Problemas Comunes

### Conflictos de Migración
```bash
# Resolver conflictos de migración
python manage.py makemigrations --merge inventory
```

### Migraciones Falsas
```bash
# Marcar migración como aplicada sin ejecutar
python manage.py migrate --fake inventory 0001

# Marcar todas las migraciones como aplicadas
python manage.py migrate --fake-initial
```

### Rollback de Migraciones
```bash
# Revertir a migración específica
python manage.py migrate inventory 0001

# Revertir todas las migraciones
python manage.py migrate inventory zero
```

## 📈 Estrategias de Migración en Producción

### Migración con Tiempo de Inactividad Mínimo
1. **Preparación**: Crear campos nuevos como opcionales
2. **Migración de datos**: Poblar nuevos campos gradualmente
3. **Validación**: Verificar integridad de datos
4. **Activación**: Hacer campos requeridos y eliminar antiguos

### Migración de Datos Masivos
```python
def migrate_large_dataset(apps, schema_editor):
    Item = apps.get_model('inventory', 'Item')
    batch_size = 1000
    
    for i in range(0, Item.objects.count(), batch_size):
        batch = Item.objects.all()[i:i+batch_size]
        for item in batch:
            # Procesar en lotes para evitar problemas de memoria
            item.new_field = process_item(item)
        Item.objects.bulk_update(batch, ['new_field'])
```

## 🔒 Seguridad en Migraciones

### Validación de Datos
```python
def validate_migration_data(apps, schema_editor):
    Item = apps.get_model('inventory', 'Item')
    
    # Validar integridad de datos antes de migración
    invalid_items = Item.objects.filter(price__lt=0)
    if invalid_items.exists():
        raise ValueError(f"Found {invalid_items.count()} items with invalid prices")
```

### Permisos y Acceso
- **Restricción de acceso**: Solo usuarios autorizados pueden ejecutar migraciones
- **Logging de operaciones**: Registrar todas las operaciones de migración
- **Auditoría de cambios**: Mantener historial de modificaciones

## 📚 Documentación y Versionado

### Convenciones de Nomenclatura
```
0001_initial.py                    # Migración inicial
0002_add_category_indexes.py       # Agregar índices de categoría
0003_modify_price_precision.py     # Modificar precisión de precios
0004_add_supplier_relationship.py # Agregar relación con proveedores
```

### Documentación de Migraciones
Cada migración compleja debe incluir:
- **Propósito**: Razón del cambio
- **Impacto**: Efectos en el sistema
- **Rollback**: Procedimiento de reversión
- **Validación**: Criterios de éxito

## 🎯 Integración con CI/CD

### Pipeline de Migraciones
```yaml
# Ejemplo de pipeline CI/CD
steps:
  - name: Check migrations
    run: python manage.py makemigrations --check --dry-run
  
  - name: Apply migrations
    run: python manage.py migrate --no-input
  
  - name: Validate data integrity
    run: python manage.py check_data_integrity
```

Este sistema de migraciones proporciona una base sólida para la evolución controlada y segura de la estructura de datos del inventario médico, garantizando la integridad y consistencia de la información a lo largo del ciclo de vida del sistema.