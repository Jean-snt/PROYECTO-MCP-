from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import json
import os
import uuid
import google.generativeai as genai
from inventory.models import Item, Order, OrderLine
from dotenv import load_dotenv


class Command(BaseCommand):
    """
    Comando de gestión para ejecutar el servidor MCP (Model Context Protocol)
    Este comando actúa como punto de entrada para el servidor MCP de la aplicación inventory.
    """
    
    help = 'Ejecuta el servidor MCP para la gestión del inventario de la Clínica Reflexo'
    
    def add_arguments(self, parser):
        """Agregar argumentos opcionales al comando"""
        parser.add_argument(
            '--port',
            type=int,
            default=8080,
            help='Puerto en el que ejecutar el servidor MCP (default: 8080)'
        )
        parser.add_argument(
            '--host',
            type=str,
            default='localhost',
            help='Host en el que ejecutar el servidor MCP (default: localhost)'
        )
    
    def handle(self, *args, **options):
        """Punto de entrada principal del comando MCP"""
        
        # Configuración inicial del servidor MCP
        host = options['host']
        port = options['port']
        
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando servidor MCP en {host}:{port}')
        )
        
        # Definición de recursos MCP disponibles
        # Estos recursos representan las entidades principales del sistema
        resources = {
            'inventory': {
                'name': 'inventory',
                'description': 'Gestión del inventario de medicamentos y productos médicos',
                'uri': 'mcp://inventory',
                'mimeType': 'application/json',
                'methods': ['GET', 'POST', 'PUT', 'DELETE']
            },
            'orders': {
                'name': 'orders',
                'description': 'Gestión de órdenes de compra y venta',
                'uri': 'mcp://orders',
                'mimeType': 'application/json',
                'methods': ['GET', 'POST', 'PUT', 'DELETE']
            },
            'health': {
                'name': 'health',
                'description': 'Estado de salud del sistema y métricas',
                'uri': 'mcp://health',
                'mimeType': 'application/json',
                'methods': ['GET']
            }
        }
        
        # Definición de herramientas MCP disponibles
        # Estas herramientas representan las acciones que se pueden ejecutar
        tools = {
            'place_order': {
                'name': 'place_order',
                'description': 'Procesa una orden de venta, descontando stock de forma atómica y consistente',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'items': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'sku': {'type': 'string'},
                                    'quantity': {'type': 'integer'}
                                },
                                'required': ['sku', 'quantity']
                            }
                        }
                    },
                    'required': ['items']
                }
            },

            'adjust_price': {
                'name': 'adjust_price',
                'description': 'Ajusta el precio de un medicamento, con validaciones para evitar saltos de precio mayores al 200%',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'sku': {'type': 'string', 'description': 'SKU del medicamento a ajustar'},
                        'new_price': {'type': 'number', 'description': 'Nuevo precio del medicamento'}
                    },
                    'required': ['sku', 'new_price']
                }
            },
            'get_item': {
                'name': 'get_item',
                'description': 'Devuelve información detallada de un medicamento por su SKU.',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'sku': {'type': 'string', 'description': 'SKU del medicamento a consultar'}
                    },
                    'required': ['sku']
                }
            },
            'rollback_order': {
                'name': 'rollback_order',
                'description': 'Revierte una orden de venta, reponiendo el stock original de los medicamentos.',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'order_code': {
                            'type': 'string',
                            'description': 'Código de la orden a revertir'
                        }
                    },
                    'required': ['order_code']
                }
            },
            'delete_medicine': {
                'name': 'delete_medicine',
                'description': 'Elimina un medicamento del inventario por su SKU, con validaciones de seguridad.',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'sku': {
                            'type': 'string',
                            'description': 'SKU del medicamento a eliminar'
                        }
                    },
                    'required': ['sku']
                }
            },
            'create_medicine': {
                'name': 'create_medicine',
                'description': 'Crea un nuevo medicamento usando la IA de Gemini con los parámetros proporcionados',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'type': {'type': 'string'},
                        'disease_category': {'type': 'string'},
                        'price': {'type': 'number'},
                        'stock': {'type': 'integer'}
                    },
                    'required': ['name', 'type', 'disease_category', 'price', 'stock']
                }
            },
            'modify_medicine': {
                'name': 'modify_medicine',
                'description': 'Modifica un campo específico de un medicamento existente',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'identifier': {
                            'type': 'string',
                            'description': 'SKU o nombre del medicamento a modificar'
                        },
                        'field': {
                            'type': 'string',
                            'description': 'Campo a modificar: sku, name, type, price, stock, status'
                        },
                        'new_value': {
                            'type': 'string',
                            'description': 'Nuevo valor para el campo'
                        }
                    },
                    'required': ['identifier', 'field', 'new_value']
                }
            }
        }
        
        # Mostrar información de configuración
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('CONFIGURACIÓN DEL SERVIDOR MCP'))
        self.stdout.write('='*60)
        
        self.stdout.write(f'Host: {host}')
        self.stdout.write(f'Puerto: {port}')
        self.stdout.write(f'Timestamp: {timezone.now()}')
        
        # Mostrar recursos disponibles
        self.stdout.write('\n' + self.style.HTTP_INFO('RECURSOS DISPONIBLES:'))
        for resource_name, resource_config in resources.items():
            self.stdout.write(f'  • {resource_name}: {resource_config["description"]}')
        
        # Mostrar herramientas disponibles
        self.stdout.write('\n' + self.style.HTTP_INFO('HERRAMIENTAS DISPONIBLES:'))
        for tool_name, tool_config in tools.items():
            self.stdout.write(f'  • {tool_name}: {tool_config["description"]}')
        
        self.stdout.write('\n' + '='*60)
        
        # Función para crear medicamentos usando Gemini AI
        def create_medicine_tool(name, type, disease_category, price, stock):
            # Cargar variables de entorno desde .env
            load_dotenv()
            
            # Obtener la API key desde las variables de entorno
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY no encontrada en las variables de entorno")
            
            # Configurar Gemini AI
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Prompt para generar el medicamento
            prompt = f"""
            Genera un medicamento con las siguientes especificaciones y devuélvelo como un objeto JSON válido:
            - name: {name}
            - type: debe ser uno de estos valores: 'pastilla', 'jarabe', 'inyectable' (elige el más apropiado para {type})
            - disease_category: {disease_category}
            - price: {price} (como número decimal)
            - stock: {stock} (como número entero)
            
            Devuelve ÚNICAMENTE el objeto JSON sin texto adicional:
            {{
                "name": "nombre del medicamento",
                "type": "pastilla/jarabe/inyectable",
                "disease_category": "categoría de enfermedad",
                "price": precio_decimal,
                "stock": stock_entero
            }}
            """
            
            try:
                # Llamar a la API de Gemini
                response = model.generate_content(prompt)
                
                # Parsear la respuesta JSON
                medicine_data = json.loads(response.text.strip())
                
                # Crear nueva instancia del modelo Item
                new_item = Item(
                    name=medicine_data['name'],
                    type=medicine_data['type'],
                    disease_category=medicine_data['disease_category'],
                    price=float(medicine_data['price']),
                    stock=int(medicine_data['stock'])
                )
                
                # Guardar en la base de datos
                new_item.save()
                
                return {
                    'success': True,
                    'message': f'Medicamento {new_item.name} creado exitosamente',
                    'item_id': new_item.id,
                    'data': medicine_data
                }
                
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Error al parsear respuesta de Gemini: {str(e)}'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Error al crear medicamento: {str(e)}'
                }
        
        # Función para procesar órdenes de venta con transacciones atómicas
        def place_order_tool(items):
            """
            Procesa una orden de venta, descontando stock de forma atómica y consistente.
            
            Args:
                items: Lista de diccionarios con 'sku' y 'quantity' para cada ítem
            
            Returns:
                dict: Resultado de la operación con código de orden y mensaje
            """
            try:
                with transaction.atomic():
                    # Generar código único para la orden
                    order_code = f"ORD-{str(uuid.uuid4())[:8].upper()}"
                    
                    # Crear nueva instancia de Order
                    new_order = Order(
                        code=order_code,
                        status='NEW',
                        total=0.0
                    )
                    new_order.save()
                    
                    total_amount = 0.0
                    order_lines = []
                    
                    # Iterar sobre los ítems de la orden
                    for item_data in items:
                        sku = item_data.get('sku')
                        quantity = int(item_data.get('quantity', 0))
                        
                        if not sku or quantity <= 0:
                            raise ValueError(f"SKU inválido o cantidad inválida: {sku}, {quantity}")
                        
                        # Buscar el ítem por SKU
                        try:
                            item = Item.objects.get(sku=sku)
                        except Item.DoesNotExist:
                            raise ValueError(f"Ítem con SKU {sku} no encontrado")
                        
                        # Verificar stock suficiente
                        if item.stock < quantity:
                            raise ValueError(
                                f"Stock insuficiente para {item.name} (SKU: {sku}). "
                                f"Stock disponible: {item.stock}, solicitado: {quantity}"
                            )
                        
                        # Actualizar stock del ítem
                        item.stock -= quantity
                        item.save()
                        
                        # Calcular totales
                        line_total = float(item.price) * quantity
                        total_amount += line_total
                        
                        # Crear OrderLine
                        order_line = OrderLine(
                            order=new_order,
                            item=item,
                            quantity=quantity,
                            unit_price=item.price,
                            line_total=line_total
                        )
                        order_line.save()
                        order_lines.append({
                            'sku': sku,
                            'name': item.name,
                            'quantity': quantity,
                            'unit_price': float(item.price),
                            'line_total': line_total
                        })
                    
                    # Actualizar el total de la orden
                    new_order.total = total_amount
                    new_order.save()
                    
                    return {
                        'success': True,
                        'message': f'Orden {order_code} procesada exitosamente',
                        'order_code': order_code,
                        'order_id': new_order.id,
                        'total': total_amount,
                        'items': order_lines
                    }
                    
            except ValueError as e:
                return {
                    'success': False,
                    'error': str(e)
                }
            except Exception as e:
                return {
                'success': False,
                'error': f'Error al procesar la orden: {str(e)}'
            }
        

        
        def adjust_price_tool(sku, new_price):
            """
            Ajusta el precio de un medicamento con validaciones de negocio.
            
            Args:
                sku (str): SKU del medicamento
                new_price (float): Nuevo precio del medicamento
            
            Returns:
                dict: Resultado de la operación
            """
            try:
                from decimal import Decimal, InvalidOperation
                from inventory.models import Item
                
                # Validar que new_price sea un número válido
                try:
                    new_price_decimal = Decimal(str(new_price))
                except (InvalidOperation, ValueError):
                    raise ValueError(f"El precio debe ser un número válido. Recibido: {new_price}")
                
                # Validar que el precio sea positivo
                if new_price_decimal <= 0:
                    raise ValueError(f"El precio debe ser mayor que cero. Recibido: {new_price_decimal}")
                
                # Buscar el medicamento por SKU
                try:
                    item = Item.objects.get(sku=sku)
                except Item.DoesNotExist:
                    raise ValueError(f"Medicamento con SKU {sku} no encontrado")
                
                # Guardar precio anterior para el mensaje
                previous_price = item.price
                
                # Validar regla de negocio: no más del 200% del precio actual
                max_allowed_price = previous_price * 2  # 200% del precio actual
                if new_price_decimal > max_allowed_price:
                    raise ValueError(
                        f"El nuevo precio ({new_price_decimal}) excede el 200% del precio actual ({previous_price}). "
                        f"Precio máximo permitido: {max_allowed_price}"
                    )
                
                # Actualizar el precio
                item.price = new_price_decimal
                item.save()
                
                return {
                    'success': True,
                    'message': f'Precio de {item.name} (SKU: {sku}) actualizado exitosamente',
                    'sku': sku,
                    'name': item.name,
                    'previous_price': float(previous_price),
                    'new_price': float(new_price_decimal),
                    'price_change_percentage': float((new_price_decimal - previous_price) / previous_price * 100)
                }
                
            except ValueError as e:
                return {
                    'success': False,
                    'error': str(e)
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Error al ajustar precio: {str(e)}'
                }
        
        def get_item_tool(sku):
            """
            Devuelve información detallada de un medicamento por su SKU.
            
            Args:
                sku (str): SKU del medicamento
            
            Returns:
                dict: Información del medicamento o error si no existe
            """
            try:
                from inventory.models import Item
                
                # Buscar el medicamento por SKU
                try:
                    item = Item.objects.get(sku=sku)
                except Item.DoesNotExist:
                    return {
                        'success': False,
                        'error': f'Medicamento con SKU {sku} no encontrado'
                    }
                
                # Devolver todos los datos del medicamento
                return {
                    'success': True,
                    'data': {
                        'sku': item.sku,
                        'name': item.name,
                        'description': item.description,
                        'price': float(item.price),
                        'stock': item.stock,
                        'created_at': item.created_at.isoformat() if item.created_at else None,
                        'updated_at': item.updated_at.isoformat() if item.updated_at else None
                    }
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Error al consultar medicamento: {str(e)}'
                }
        
        def rollback_order_tool(order_code):
            """
            Revierte una orden de venta, reponiendo el stock original de los medicamentos.
            
            Args:
                order_code (str): Código de la orden a revertir
                
            Returns:
                dict: Resultado de la operación
            """
            from django.db import transaction
            from inventory.models import Order, OrderLine, Item
            
            try:
                # Buscar la orden por su código
                try:
                    order = Order.objects.get(order_code=order_code)
                except Order.DoesNotExist:
                    return {
                        'success': False,
                        'error': f'Orden con código {order_code} no encontrada'
                    }
                
                # Verificar que el estado no sea CANCELLED o ROLLEDBACK
                if order.status in ['CANCELLED', 'ROLLEDBACK']:
                    return {
                        'success': False,
                        'error': f'La orden {order_code} ya está en estado {order.status} y no puede ser revertida'
                    }
                
                # Realizar la operación dentro de una transacción atómica
                with transaction.atomic():
                    # Iterar sobre todas las líneas de la orden
                    order_lines = OrderLine.objects.filter(order=order)
                    
                    for order_line in order_lines:
                        # Buscar el item correspondiente
                        item = order_line.item
                        
                        # Restaurar el stock sumando la cantidad original
                        item.stock += order_line.quantity
                        item.save()
                    
                    # Actualizar el estado de la orden a ROLLEDBACK
                    order.status = 'ROLLEDBACK'
                    order.save()
                
                return {
                    'success': True,
                    'message': f'Orden {order_code} revertida exitosamente. Stock restaurado para {order_lines.count()} productos.'
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Error al revertir orden: {str(e)}'
                }
        
        def delete_medicine_tool(sku):
            """
            Elimina un medicamento del inventario por su SKU.
            
            Args:
                sku (str): SKU del medicamento a eliminar
                
            Returns:
                dict: Resultado de la operación
            """
            try:
                from inventory.models import Item, OrderLine
                
                # Buscar el medicamento por SKU
                try:
                    item = Item.objects.get(sku=sku)
                except Item.DoesNotExist:
                    return {
                        'success': False,
                        'error': f'Medicamento con SKU {sku} no encontrado'
                    }
                
                # Verificar si el medicamento tiene órdenes asociadas
                order_lines = OrderLine.objects.filter(item=item)
                if order_lines.exists():
                    return {
                        'success': False,
                        'error': f'No se puede eliminar el medicamento {item.name} (SKU: {sku}) porque tiene órdenes asociadas. Primero debe revertir las órdenes relacionadas.'
                    }
                
                # Guardar información del medicamento antes de eliminarlo
                medicine_name = item.name
                medicine_sku = item.sku
                
                # Eliminar el medicamento
                item.delete()
                
                return {
                    'success': True,
                    'message': f'Medicamento {medicine_name} (SKU: {medicine_sku}) eliminado exitosamente del inventario',
                    'deleted_item': {
                        'sku': medicine_sku,
                        'name': medicine_name
                    }
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Error al eliminar medicamento: {str(e)}'
                }
        
        def modify_medicine_tool(identifier=None, field=None, new_value=None, step=None):
            """
            Modifica un campo específico de un medicamento existente de forma interactiva
            
            Args:
                identifier: SKU o nombre del medicamento (opcional para modo interactivo)
                field: Campo a modificar (sku, name, type, price, stock, status) (opcional)
                new_value: Nuevo valor para el campo (opcional)
                step: Paso actual del proceso interactivo (opcional)
            
            Returns:
                dict: Resultado de la operación o solicitud de información
            """
            try:
                # Paso 1: Solicitar identificador si no se proporciona
                if not identifier:
                    return {
                        'success': True,
                        'interactive': True,
                        'step': 'request_identifier',
                        'message': '🔍 **Paso 1/3: Identificar medicamento**\n\nPor favor, proporciona el **SKU** o **nombre** del medicamento que deseas modificar.\n\n**Ejemplo:** MED001 o "Aspirina 500mg"',
                        'help': 'Puedes usar el SKU (código único) o el nombre completo del medicamento'
                    }
                
                # Buscar el medicamento
                try:
                    medicine = Item.objects.get(sku=identifier)
                except Item.DoesNotExist:
                    try:
                        medicine = Item.objects.get(name=identifier)
                    except Item.DoesNotExist:
                        # Buscar medicamentos similares
                        similar_medicines = Item.objects.filter(name__icontains=identifier)[:3]
                        if similar_medicines:
                            suggestions = '\n'.join([f'• **{med.name}** (SKU: {med.sku})' for med in similar_medicines])
                            return {
                                'success': False,
                                'error': f'❌ No se encontró ningún medicamento con SKU o nombre: "{identifier}"',
                                'suggestions': f'**¿Te refieres a alguno de estos?**\n{suggestions}',
                                'interactive': True,
                                'step': 'request_identifier'
                            }
                        else:
                            return {
                                'success': False,
                                'error': f'❌ No se encontró ningún medicamento con SKU o nombre: "{identifier}"',
                                'interactive': True,
                                'step': 'request_identifier'
                            }
                
                # Paso 2: Solicitar campo si no se proporciona
                if not field:
                    return {
                        'success': True,
                        'interactive': True,
                        'step': 'request_field',
                        'message': f'📋 **Paso 2/3: Seleccionar campo**\n\n**Medicamento encontrado:** {medicine.name} (SKU: {medicine.sku})\n\n**Campos disponibles:**\n• **sku** - Código único\n• **name** - Nombre del medicamento\n• **type** - Tipo de medicamento\n• **price** - Precio\n• **stock** - Cantidad en inventario\n• **status** - Estado (active/inactive/discontinued)\n\n¿Qué campo deseas modificar?',
                        'help': 'Selecciona uno de los campos disponibles',
                        'medicine_info': {
                            'sku': medicine.sku,
                            'name': medicine.name,
                            'type': medicine.type,
                            'price': str(medicine.price),
                            'stock': medicine.stock,
                            'status': medicine.status
                        }
                    }
                
                # Validar el campo
                valid_fields = ['sku', 'name', 'type', 'price', 'stock', 'status']
                if field not in valid_fields:
                    return {
                        'success': False,
                        'error': f'❌ Campo inválido: "{field}"\n\n**Campos válidos:** {', '.join(valid_fields)}',
                        'interactive': True,
                        'step': 'request_field'
                    }
                
                # Paso 3: Solicitar nuevo valor si no se proporciona
                if new_value is None:
                    current_value = getattr(medicine, field)
                    field_descriptions = {
                        'sku': 'código único del medicamento',
                        'name': 'nombre del medicamento',
                        'type': 'tipo de medicamento',
                        'price': 'precio del medicamento',
                        'stock': 'cantidad en inventario',
                        'status': 'estado del medicamento (active/inactive/discontinued)'
                    }
                    
                    return {
                        'success': True,
                        'interactive': True,
                        'step': 'request_value',
                        'message': f'📝 **Paso 3/3: Nuevo valor**\n\n**Campo a modificar:** {field}\n**Valor actual:** {current_value}\n\nPor favor, proporciona el nuevo {field_descriptions[field]}.\n\n**Ejemplo:** {_get_field_example(field)}',
                        'help': f'Ingresa el nuevo valor para {field}',
                        'field_info': {
                            'field': field,
                            'current_value': str(current_value),
                            'medicine_name': medicine.name,
                            'medicine_sku': medicine.sku
                        }
                    }
                
                # Guardar valores anteriores para el mensaje
                old_value = getattr(medicine, field)
                
                # Validaciones específicas por campo
                if field == 'sku':
                    if Item.objects.filter(sku=new_value).exclude(id=medicine.id).exists():
                        return {
                            'success': False,
                            'error': f'❌ Ya existe un medicamento con el SKU: {new_value}',
                            'interactive': True,
                            'step': 'request_value'
                        }
                elif field == 'price':
                    try:
                        new_value = float(new_value)
                        if new_value < 0:
                            return {
                                'success': False,
                                'error': '❌ El precio no puede ser negativo',
                                'interactive': True,
                                'step': 'request_value'
                            }
                    except ValueError:
                        return {
                            'success': False,
                            'error': '❌ El precio debe ser un número válido (ejemplo: 15.50)',
                            'interactive': True,
                            'step': 'request_value'
                        }
                elif field == 'stock':
                    try:
                        new_value = int(new_value)
                        if new_value < 0:
                            return {
                                'success': False,
                                'error': '❌ El stock no puede ser negativo',
                                'interactive': True,
                                'step': 'request_value'
                            }
                    except ValueError:
                        return {
                            'success': False,
                            'error': '❌ El stock debe ser un número entero válido (ejemplo: 100)',
                            'interactive': True,
                            'step': 'request_value'
                        }
                elif field == 'status':
                    valid_statuses = ['active', 'inactive', 'discontinued']
                    if new_value not in valid_statuses:
                        return {
                            'success': False,
                            'error': f'❌ Estado inválido: "{new_value}"\n\n**Estados válidos:** {', '.join(valid_statuses)}',
                            'interactive': True,
                            'step': 'request_value'
                        }
                
                # Aplicar la modificación
                setattr(medicine, field, new_value)
                medicine.save()
                
                return {
                    'success': True,
                    'message': f'✅ **Medicamento modificado exitosamente**\n\n**Medicamento:** {medicine.name}\n**Campo:** {field}\n**Valor anterior:** {old_value}\n**Valor nuevo:** {new_value}',
                    'modified_item': {
                        'sku': medicine.sku,
                        'name': medicine.name,
                        'field_modified': field,
                        'old_value': str(old_value),
                        'new_value': str(new_value)
                    }
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f'❌ Error al modificar medicamento: {str(e)}'
                }
        
        def _get_field_example(field):
            """Devuelve un ejemplo para cada tipo de campo"""
            examples = {
                'sku': 'MED001',
                'name': 'Aspirina 500mg',
                'type': 'pastilla',
                'price': '15.50',
                'stock': '100'
            }
            return examples.get(field, 'valor')
        
        # Guardar configuración para uso futuro
        mcp_config = {
            'server': {
                'host': host,
                'port': port,
                'started_at': timezone.now().isoformat()
            },
            'resources': resources,
            'tools': tools
        }
        
        # TODO: Aquí se implementará la lógica del servidor MCP real
        # Por ahora, solo mostramos la configuración preparada
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nEsqueleto del servidor MCP configurado exitosamente.\n'
                'La implementación completa del servidor se agregará en futuras iteraciones.'
            )
        )
        
        # Configuración guardada internamente para uso futuro
        # return mcp_config  # No retornamos nada en comandos de Django