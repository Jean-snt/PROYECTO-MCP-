from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
import json
import os
import uuid
import re
import google.generativeai as genai
from dotenv import load_dotenv
from .models import Item, Order, OrderLine

# Create your views here.
def item_list(request):
    items = Item.objects.all()
    return render(request, 'inventory/item_list.html', {'items': items})

def dashboard(request):
    """Vista del dashboard principal con inventario y chatbot"""
    items = Item.objects.all()
    return render(request, 'inventory/dashboard.html', {'items': items})

def normalize_text(text):
    """Normaliza el texto del usuario para mejorar el reconocimiento de intenciones"""
    if not text:
        return ""
    
    # Convertir a minúsculas
    text = text.lower()
    
    # Eliminar signos de puntuación y espacios extra
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar espacios al inicio y final
    return text.strip()

def recognize_intent(message):
    """Reconoce la intención del usuario basado en palabras clave con prioridad mejorada"""
    normalized_message = normalize_text(message)
    
    # Verificar intenciones específicas primero (orden de prioridad)
    # Eliminar medicamento - verificar primero
    if any(word in normalized_message for word in ['eliminar', 'borrar', 'quitar', 'remover', 'delete']):
        if any(word in normalized_message for word in ['medicamento', 'medicina', 'producto']):
            return 'delete_medicine'
    
    # Modificar medicamento - más flexible
    if any(word in normalized_message for word in ['modificar', 'editar', 'alterar', 'cambiar', 'actualizar']):
        if any(word in normalized_message for word in ['medicamento', 'medicina', 'producto']) or not any(word in normalized_message for word in ['precio', 'pedido', 'orden']):
            return 'modify_medicine'
    
    # Crear medicamento - más flexible
    if any(word in normalized_message for word in ['crear', 'nuevo', 'agregar', 'añadir', 'crea', 'registrar']):
        if any(word in normalized_message for word in ['medicamento', 'medicina', 'producto']) or 'nuevo' in normalized_message:
            return 'create_medicine'
    
    # Consultar item
    if any(word in normalized_message for word in ['obtener', 'ver', 'mostrar', 'buscar', 'consultar', 'sku', 'informacion', 'info']):
        return 'get_item'
    
    # Pedido/orden
    if any(word in normalized_message for word in ['pedido', 'orden', 'comprar', 'solicitar', 'pedir']):
        return 'place_order'
    
    # Ajustar precio
    if any(word in normalized_message for word in ['precio', 'ajustar']) and not any(word in normalized_message for word in ['eliminar', 'modificar', 'crear']):
        return 'adjust_price'
    
    # Revertir orden
    if any(word in normalized_message for word in ['revertir', 'cancelar', 'rollback', 'deshacer', 'anular']) and any(word in normalized_message for word in ['pedido', 'orden']):
        return 'rollback_order'
    
    return None

def get_help_message():
    """Devuelve un mensaje de ayuda con los comandos disponibles"""
    return {
        'success': False,
        'error': 'No pude entender tu comando.',
        'help': {
            'message': '''¡Hola! Soy tu asistente de inventario. Puedo ayudarte con:\n\n• **Crear nuevos medicamentos**\n• **Modificar medicamento**\n• **Eliminar medicamento**\n\n**Ejemplos de comandos:**\n- "crear medicamento Aspirina tipo pastilla categoria dolor precio 15.00 stock 50"\n- "modificar medicamento"\n- "eliminar medicamento SKU-5"\n\n💡 **Tip:** Escribe de forma natural, entiendo diferentes variaciones de los comandos.'''
        }
    }

@csrf_exempt
@require_POST
def chatbot_endpoint(request):
    """Endpoint para manejar peticiones del chatbot del dashboard"""
    try:
        # Parsear el JSON de la petición
        data = json.loads(request.body)
        tool_name = data.get('tool_name')
        parameters = data.get('parameters', {})
        
        # Validar que se proporcione el nombre de la herramienta
        if not tool_name:
            return JsonResponse({
                'success': False,
                'error': 'Se requiere especificar tool_name'
            }, status=400)
        
        # Mapear las herramientas disponibles
        available_tools = {
            'create_medicine': create_medicine_tool,
            'place_order': place_order_tool,
            'adjust_price': adjust_price_tool,
            'get_item': get_item_tool,
            'rollback_order': rollback_order_tool,
            'delete_medicine': delete_medicine_tool,
            'modify_medicine': modify_medicine_tool
        }
        
        # Verificar si la herramienta existe
        if tool_name not in available_tools:
            return JsonResponse({
                'success': False,
                'error': f'Herramienta {tool_name} no disponible. Herramientas disponibles: {", ".join(available_tools.keys())}'
            }, status=400)
        
        # Ejecutar la herramienta correspondiente
        tool_function = available_tools[tool_name]
        
        # Llamar a la función con los parámetros apropiados
        if tool_name == 'create_medicine':
            name = parameters.get('name')
            medicine_type = parameters.get('type')
            disease_category = parameters.get('disease_category')
            price = parameters.get('price')
            stock = parameters.get('stock')
            
            if not all([name, medicine_type, disease_category, price is not None, stock is not None]):
                return JsonResponse({
                    'success': False,
                    'error': 'Faltan parámetros requeridos: name, type, disease_category, price, stock'
                }, status=400)
            
            result = tool_function(name, medicine_type, disease_category, price, stock)
            
        elif tool_name == 'place_order':
            items = parameters.get('items', [])
            
            if not items or not isinstance(items, list):
                return JsonResponse({
                    'success': False,
                    'error': 'Se requiere una lista de items válida'
                }, status=400)
            
            result = tool_function(items)
            

        elif tool_name == 'adjust_price':
            sku = parameters.get('sku')
            new_price = parameters.get('new_price')
            
            if not sku or new_price is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Se requieren los parámetros sku y new_price'
                }, status=400)
            
            try:
                new_price = float(new_price)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'new_price debe ser un número válido'
                }, status=400)
            
            result = tool_function(sku, new_price)
            
        elif tool_name == 'get_item':
            sku = parameters.get('sku')
            
            if not sku:
                return JsonResponse({
                    'success': False,
                    'error': 'Se requiere el parámetro sku'
                }, status=400)
            
            result = tool_function(sku)
            
        elif tool_name == 'rollback_order':
            order_code = parameters.get('order_code')
            
            if not order_code:
                return JsonResponse({
                    'success': False,
                    'error': 'Se requiere el parámetro order_code'
                }, status=400)
            
            result = tool_function(order_code)
        
        # Asegurar que el resultado siempre tenga la estructura correcta
        if isinstance(result, dict) and 'success' in result:
            return JsonResponse(result)
        else:
            # Si la herramienta no devuelve el formato esperado, envolver en estructura estándar
            return JsonResponse({
                'success': True,
                'data': result
            })
        
    except json.JSONDecodeError as e:
        return JsonResponse({
            'success': False,
            'error': f'JSON inválido en la petición: {str(e)}'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': f'Error de validación: {str(e)}'
        }, status=400)
    except Exception as e:
        # Log del error para debugging (en producción usar logging)
        import traceback
        error_details = traceback.format_exc()
        
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}',
            'details': error_details if hasattr(e, '__traceback__') else None
        }, status=500)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotIntelligentView(View):
    def post(self, request):
        return chatbot_intelligent_logic(request)

def chatbot_intelligent_logic(request):
    """Endpoint inteligente para el chatbot con reconocimiento de intenciones y estados conversacionales"""
    try:
        # Parsear el JSON de la petición
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        context = data.get('context', None)
        
        # Validar que se proporcione un mensaje
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Se requiere proporcionar un mensaje'
            }, status=400)
        
        # Inicializar estado de conversación en la sesión
        request.session.setdefault('chatbot_state', {'action': None, 'data': {}})
        chatbot_state = request.session['chatbot_state']
        
        # Verificar si hay un estado activo
        current_action = chatbot_state.get('action')
        
        # Permitir cancelar/reiniciar en cualquier momento
        escape_commands = ['cancelar', 'cancel', 'salir', 'exit', 'terminar', 'olvidar', 'empezar de nuevo', 'reiniciar', 'reset', 'nuevo']
        if normalize_text(message) in escape_commands:
            # Limpiar completamente el estado de la sesión
            request.session['chatbot_state'] = {'action': None, 'data': {}}
            return JsonResponse({
                'success': True,
                'message': 'Ok, he olvidado la conversación actual. ¿En qué puedo ayudarte ahora?',
                'help': 'Puedes crear, modificar o eliminar medicamentos.'
            })
        
        # Priorizar nuevas intenciones sobre estados activos
        new_intent = recognize_intent(message)
        if new_intent and current_action:
            # Si hay una nueva intención clara, sobrescribir el estado actual
            clear_intents = ['create_medicine', 'delete_medicine', 'modify_medicine']
            if new_intent in clear_intents:
                # Limpiar estado anterior y procesar nueva intención
                request.session['chatbot_state'] = {'action': None, 'data': {}}
                current_action = None  # Resetear para procesar la nueva intención
        
        # Manejar estados conversacionales activos
        if current_action == 'esperando_sku_modificar':
            # El usuario proporcionó el SKU/nombre del medicamento
            result = get_item_tool(message)
            if result.get('success'):
                # Medicamento encontrado, cambiar estado
                chatbot_state['action'] = 'esperando_campo_modificar'
                chatbot_state['data']['identifier'] = message
                chatbot_state['data']['medicine_info'] = result.get('item')
                request.session['chatbot_state'] = chatbot_state
                
                return JsonResponse({
                    'success': False,
                    'interactive': True,
                    'tool': 'modify_medicine',
                    'step': 'awaiting_field',
                    'message': f"Medicamento encontrado: {result.get('item', {}).get('name', 'N/A')}. ¿Qué campo deseas modificar?",
                    'help': "Campos disponibles: nombre, tipo, categoria, precio, stock",
                    'medicine_info': result.get('item')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'interactive': True,
                    'tool': 'modify_medicine',
                    'step': 'awaiting_medicine',
                    'message': f"No encontré el medicamento '{message}'. Por favor, proporciona un SKU válido o nombre exacto.",
                    'help': "Ejemplos: 'SKU-1', 'Aspirina', 'Paracetamol 500mg'"
                })
        
        elif current_action == 'esperando_campo_modificar':
            # El usuario proporcionó el campo a modificar
            valid_fields = ['nombre', 'name', 'tipo', 'type', 'categoria', 'category', 'precio', 'price', 'stock']
            field_normalized = normalize_text(message)
            
            # Mapear campos en español a inglés
            field_mapping = {
                'nombre': 'name',
                'tipo': 'type', 
                'categoria': 'category',
                'precio': 'price',
                'stock': 'stock'
            }
            
            field = field_mapping.get(field_normalized, field_normalized)
            
            if field in ['name', 'type', 'category', 'price', 'stock']:
                chatbot_state['action'] = 'esperando_valor_modificar'
                chatbot_state['data']['field'] = field
                request.session['chatbot_state'] = chatbot_state
                
                field_examples = {
                    'name': 'Ejemplo: Aspirina 500mg',
                    'type': 'Ejemplos: pastilla, jarabe, inyección, crema',
                    'category': 'Ejemplos: dolor, fiebre, infección, alergia',
                    'price': 'Ejemplo: 15.50',
                    'stock': 'Ejemplo: 100'
                }
                
                return JsonResponse({
                    'success': False,
                    'interactive': True,
                    'tool': 'modify_medicine',
                    'step': 'awaiting_value',
                    'message': f"¿Cuál es el nuevo valor para {field}?",
                    'help': field_examples.get(field, 'Proporciona el nuevo valor')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'interactive': True,
                    'tool': 'modify_medicine',
                    'step': 'awaiting_field',
                    'message': f"Campo '{message}' no válido. ¿Qué campo deseas modificar?",
                    'help': "Campos disponibles: nombre, tipo, categoria, precio, stock"
                })
        
        elif current_action == 'esperando_valor_modificar':
            # El usuario proporcionó el nuevo valor
            identifier = chatbot_state['data'].get('identifier')
            field = chatbot_state['data'].get('field')
            
            # Procesar la modificación
            result = modify_medicine_tool(identifier=identifier, field=field, new_value=message, step='complete')
            
            # Resetear el estado
            request.session['chatbot_state'] = {'action': None, 'data': {}}
            
            return JsonResponse(result)
        
        # Reconocer la intención del usuario (puede ser nueva o continuación)
        intent = new_intent if new_intent else recognize_intent(message)
        
        # Si no se reconoce ninguna intención, verificar si hay estado activo
        if not intent:
            if current_action:
                return JsonResponse({
                    'success': False,
                    'interactive': True,
                    'message': f"Aún estamos en el proceso de {current_action.replace('_', ' ')}. Por favor, completa la tarea actual.",
                    'help': "Proporciona la información solicitada o escribe 'cancelar', 'olvidar' o 'empezar de nuevo' para reiniciar."
                })
            else:
                return JsonResponse(get_help_message(), status=400)
        
        # Mapear las herramientas disponibles
        available_tools = {
            'create_medicine': create_medicine_tool,
            'place_order': place_order_tool,
            'adjust_price': adjust_price_tool,
            'get_item': get_item_tool,
            'rollback_order': rollback_order_tool,
            'delete_medicine': delete_medicine_tool,
            'modify_medicine': modify_medicine_tool
        }
        
        # Para intenciones que requieren parámetros específicos, solicitar más información
        if intent == 'create_medicine':
            # Extraer parámetros usando regex (re ya importado al inicio del archivo)
            
            # Normalizar el mensaje para la extracción de parámetros
            normalized_message = normalize_text(message)
            
            # Patrones para extraer información
            name_match = re.search(r'medicamento\s+(\w+)', normalized_message)
            type_match = re.search(r'tipo\s+(\w+)', normalized_message)
            category_match = re.search(r'categoria\s+(\w+)', normalized_message)
            price_match = re.search(r'precio\s+([\d.]+)', normalized_message)
            stock_match = re.search(r'stock\s+(\d+)', normalized_message)
            
            if all([name_match, type_match, category_match, price_match, stock_match]):
                # Todos los parámetros encontrados, procesar la herramienta
                try:
                    name = name_match.group(1)
                    medicine_type = type_match.group(1)
                    disease_category = category_match.group(1)
                    price = float(price_match.group(1))
                    stock = int(stock_match.group(1))
                    
                    # Llamar a la herramienta create_medicine
                    result = available_tools['create_medicine'](name, medicine_type, disease_category, price, stock)
                    return JsonResponse(result)
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'error': f'Error al crear medicamento: {str(e)}'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Para crear un medicamento necesito más información.',
                    'help': {
                        'message': '''Para crear un nuevo medicamento, necesito la siguiente información:\n\n**Formato:**\ncrear medicamento [NOMBRE] tipo [TIPO] categoria [CATEGORIA] precio [PRECIO] stock [CANTIDAD]\n\n**Ejemplo:**\ncrear medicamento Ibuprofeno tipo pastilla categoria dolor precio 12.50 stock 100\n\n**Tipos disponibles:** pastilla, jarabe, inyección, crema\n**Categorías disponibles:** dolor, fiebre, infección, alergia'''
                    }
                }, status=400)
        
        elif intent == 'get_item':
            # Buscar SKU en el mensaje
            sku_pattern = r'SKU-?(\d+)'
            sku_match = re.search(sku_pattern, message.upper())
            
            if sku_match:
                sku_id = sku_match.group(1)  # Extraer solo el número
                sku = f'SKU-{sku_id}'  # Formatear como SKU-X
                result = available_tools[intent](sku)
                return JsonResponse(result)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Para consultar un medicamento necesito el SKU.',
                    'help': {
                        'message': '''Para consultar información de un medicamento:\n\n**Formato:**\nobtener medicamento SKU-[NÚMERO]\n\n**Ejemplo:**\nobtener medicamento SKU-5\n\n**Nota:** El SKU es el identificador único del medicamento que aparece en la tabla de inventario.'''
                    }
                }, status=400)
        
        elif intent == 'delete_medicine':
            # Buscar SKU en el mensaje
            sku_match = re.search(r'SKU-?(\d+)', message.upper())
            if sku_match:
                sku_id = sku_match.group(1)
                sku = f'SKU-{sku_id}'
                result = available_tools[intent](sku)
                return JsonResponse(result)
            else:
                # Si no hay SKU, buscar un nombre de medicamento
                # Extraer palabras después de "eliminar" que no sean palabras comunes
                words = message.lower().split()
                stop_words = {'eliminar', 'medicamento', 'medicina', 'producto', 'el', 'la', 'un', 'una', 'de', 'del'}
                medicine_words = [word for word in words if word not in stop_words and len(word) > 2]
                
                if medicine_words:
                    # Intentar con el nombre completo restante
                    medicine_name = ' '.join(medicine_words)
                    result = available_tools[intent](medicine_name)
                    return JsonResponse(result)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Para eliminar un medicamento necesito el SKU o el nombre del medicamento.',
                        'help': {
                            'message': '''Para eliminar un medicamento:\n\n**Por SKU:**\neliminar medicamento SKU-[NÚMERO]\n\n**Por nombre:**\neliminar medicamento [NOMBRE_EXACTO]\n\n**Ejemplos:**\neliminar medicamento SKU-5\neliminar medicamento Aspirina\neliminar medicamento Paracetamol 500mg\n\n**Nota:** Si el medicamento no tiene SKU, usa el nombre exacto como aparece en la tabla.'''
                        }
                    }, status=400)
        
        elif intent == 'modify_medicine':
            # Iniciar el proceso de modificación estableciendo el estado
            chatbot_state['action'] = 'esperando_sku_modificar'
            chatbot_state['data'] = {}
            request.session['chatbot_state'] = chatbot_state
            
            return JsonResponse({
                'success': False,
                'interactive': True,
                'tool': 'modify_medicine',
                'step': 'awaiting_medicine',
                'message': 'Por favor, proporciona el SKU o nombre exacto del medicamento que deseas modificar.',
                'help': "Ejemplos: 'SKU-1', 'Aspirina', 'Paracetamol 500mg'"
            })
        
        # Para otras intenciones, solicitar parámetros específicos
        return JsonResponse({
            'success': False,
            'error': f'Reconocí que quieres usar la función "{intent}", pero necesito más información específica.',
            'help': {
                'message': 'Por favor, proporciona los parámetros necesarios para esta operación.',
                'intent_recognized': intent
            }
        }, status=400)
        
    except json.JSONDecodeError as e:
        return JsonResponse({
            'success': False,
            'error': f'JSON inválido en la petición: {str(e)}'
        }, status=400)
    except Exception as e:
        # Log del error para debugging
        import traceback
        error_details = traceback.format_exc()
        
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}',
            'details': error_details if hasattr(e, '__traceback__') else None
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def mcp_tool_use(request):
    """Endpoint para manejar peticiones de herramientas MCP"""
    try:
        # Parsear el JSON de la petición
        data = json.loads(request.body)
        tool_name = data.get('tool_name')
        parameters = data.get('parameters', {})
        
        if tool_name == 'create_medicine':
            # Extraer parámetros
            name = parameters.get('name')
            medicine_type = parameters.get('type')
            disease_category = parameters.get('disease_category')
            price = parameters.get('price')
            stock = parameters.get('stock')
            
            # Validar parámetros requeridos
            if not all([name, medicine_type, disease_category, price is not None, stock is not None]):
                return JsonResponse({
                    'success': False,
                    'error': 'Faltan parámetros requeridos: name, type, disease_category, price, stock'
                }, status=400)
            
            # Llamar a la función create_medicine_tool
            result = create_medicine_tool(name, medicine_type, disease_category, price, stock)
            return JsonResponse(result)
        
        elif tool_name == 'place_order':
            # Extraer parámetros
            items = parameters.get('items', [])
            
            # Validar parámetros requeridos
            if not items or not isinstance(items, list):
                return JsonResponse({
                    'success': False,
                    'error': 'Se requiere una lista de items válida'
                }, status=400)
            
            # Validar estructura de cada item
            for item in items:
                if not isinstance(item, dict) or 'sku' not in item or 'quantity' not in item:
                    return JsonResponse({
                        'success': False,
                        'error': 'Cada item debe tener sku y quantity'
                    }, status=400)
            
            # Llamar a la función place_order_tool
            result = place_order_tool(items)
            return JsonResponse(result)
        

        elif tool_name == 'adjust_price':
            # Extraer parámetros
            sku = parameters.get('sku')
            new_price = parameters.get('new_price')
            
            # Validar parámetros requeridos
            if not sku or new_price is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Se requieren los parámetros sku y new_price'
                }, status=400)
            
            # Llamar a la función adjust_price_tool
            result = adjust_price_tool(sku, new_price)
            return JsonResponse(result)
        
        elif tool_name == 'get_item':
            # Extraer parámetros
            sku = parameters.get('sku')
            
            # Validar parámetros requeridos
            if not sku:
                return JsonResponse({
                    'success': False,
                    'error': 'El parámetro sku es requerido'
                }, status=400)
            
            # Llamar a la función get_item_tool
            result = get_item_tool(sku)
            return JsonResponse(result)
        
        elif tool_name == 'rollback_order':
            # Extraer parámetros
            order_code = parameters.get('order_code')
            
            # Validar parámetros requeridos
            if not order_code:
                return JsonResponse({
                    'success': False,
                    'error': 'El parámetro order_code es requerido'
                }, status=400)
            
            # Llamar a la función rollback_order_tool
            result = rollback_order_tool(order_code)
            return JsonResponse(result)
        
        elif tool_name == 'delete_medicine':
            # Extraer parámetros
            sku = parameters.get('sku')
            
            # Validar parámetros requeridos
            if not sku:
                return JsonResponse({
                    'success': False,
                    'error': 'El parámetro sku es requerido'
                }, status=400)
            
            # Llamar a la función delete_medicine_tool
            result = delete_medicine_tool(sku)
            return JsonResponse(result)
        
        elif tool_name == 'modify_medicine':
            # Extraer parámetros (ahora todos son opcionales para el modo interactivo)
            identifier = parameters.get('identifier')
            field = parameters.get('field')
            new_value = parameters.get('new_value')
            step = parameters.get('step')
            
            # Llamar a la función modify_medicine_tool con todos los parámetros
            result = modify_medicine_tool(identifier=identifier, field=field, new_value=new_value, step=step)
            return JsonResponse(result)
        
        else:
            return JsonResponse({
                'success': False,
                'error': f'Herramienta no reconocida: {tool_name}'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido en el cuerpo de la petición'
        }, status=400)
    except json.JSONDecodeError as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al parsear JSON: {str(e)}'
        }, status=400)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error en chatbot_intelligent_endpoint: {error_details}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)

def create_medicine_tool(name, medicine_type, disease_category, price, stock):
    """Función para crear medicamentos usando Gemini AI"""
    # Cargar variables de entorno desde .env
    load_dotenv()
    
    # Obtener la API key desde las variables de entorno
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {
            'success': False,
            'error': 'GEMINI_API_KEY no encontrada en las variables de entorno'
        }
    
    # Configurar Gemini AI
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt para generar el medicamento
    prompt = f"""
    Genera un medicamento con las siguientes especificaciones y devuélvelo como un objeto JSON válido:
    - name: {name}
    - type: debe ser uno de estos valores: 'pastilla', 'jarabe', 'inyectable' (elige el más apropiado para {medicine_type})
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
        
        # Limpiar y extraer JSON de la respuesta
        response_text = response.text.strip()
        
        # Buscar el JSON en la respuesta (puede venir con texto adicional)
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            return {
                'success': False,
                'error': f'No se encontró JSON válido en la respuesta de Gemini: {response_text}'
            }
        
        json_str = response_text[start_idx:end_idx]
        
        # Parsear la respuesta JSON
        medicine_data = json.loads(json_str)
        
        # Generar SKU único
        import uuid
        sku = f"MED-{str(uuid.uuid4())[:8].upper()}"
        
        # Crear nueva instancia del modelo Item
        new_item = Item(
            sku=sku,
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
                'type': item.type,
                'disease_category': item.disease_category,
                'price': float(item.price),
                'stock': item.stock,
                'version': item.version
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
    
    try:
        # Buscar la orden por su código
        try:
            order = Order.objects.get(code=order_code)
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

def delete_medicine_tool(identifier):
    """
    Elimina un medicamento del inventario por su SKU o nombre.
    
    Args:
        identifier (str): SKU o nombre del medicamento a eliminar
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        # Buscar el medicamento por SKU o nombre
        item = None
        
        # Primero intentar buscar por SKU
        try:
            item = Item.objects.get(sku=identifier)
        except Item.DoesNotExist:
            # Si no se encuentra por SKU, buscar por nombre
            try:
                item = Item.objects.get(name__iexact=identifier)
            except Item.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Medicamento con SKU o nombre "{identifier}" no encontrado'
                }
        
        # Verificar si el medicamento tiene órdenes asociadas
        order_lines = OrderLine.objects.filter(item=item)
        if order_lines.exists():
            return {
                'success': False,
                'error': f'No se puede eliminar el medicamento {item.name} (SKU: {item.sku or "N/A"}) porque tiene órdenes asociadas. Primero debe revertir las órdenes relacionadas.'
            }
        
        # Guardar información del medicamento antes de eliminarlo
        medicine_name = item.name
        medicine_sku = item.sku or "N/A"
        
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
        identifier: SKU o nombre del medicamento (opcional en modo interactivo)
        field: Campo a modificar (opcional en modo interactivo)
        new_value: Nuevo valor para el campo (opcional en modo interactivo)
        step: Paso actual del proceso interactivo
    
    Returns:
        dict: Resultado de la operación o solicitud de información
    """
    try:
        # Modo interactivo: solicitar identificador del medicamento
        if not identifier:
            return {
                'success': False,
                'interactive': True,
                'tool': 'modify_medicine',
                'step': 'awaiting_medicine',
                'message': '🔍 **Paso 1/3: Identificar medicamento**\n\nPor favor, proporciona el **SKU** o **nombre exacto** del medicamento que deseas modificar.\n\n**Ejemplos:**\n• "MED001"\n• "Aspirina"\n• "Paracetamol 500mg"',
                'help': 'Escribe el SKU o nombre del medicamento',
                'context_data': {}
            }
        
        # Buscar el medicamento
        medicine = None
        try:
            medicine = Item.objects.get(sku=identifier)
        except Item.DoesNotExist:
            try:
                medicine = Item.objects.get(name__iexact=identifier)
            except Item.DoesNotExist:
                # Buscar medicamentos similares para sugerir
                similar_medicines = Item.objects.filter(name__icontains=identifier)[:5]
                if similar_medicines:
                    suggestions = '\n'.join([f'• {med.name} (SKU: {med.sku})' for med in similar_medicines])
                    return {
                        'success': False,
                        'interactive': True,
                        'step': 'request_identifier',
                        'message': f'❌ No se encontró el medicamento "{identifier}".\n\n**¿Te refieres a alguno de estos?**\n{suggestions}\n\nPor favor, proporciona el SKU o nombre exacto.',
                        'help': 'Usa el SKU o nombre exacto del medicamento'
                    }
                else:
                    return {
                        'success': False,
                        'interactive': True,
                        'step': 'request_identifier',
                        'message': f'❌ No se encontró ningún medicamento con "{identifier}".\n\nVerifica que el SKU o nombre sea correcto.',
                        'help': 'Verifica el SKU o nombre del medicamento'
                    }
        
        # Modo interactivo: solicitar campo a modificar
        if not field:
            return {
                'success': False,
                'interactive': True,
                'tool': 'modify_medicine',
                'step': 'awaiting_field',
                'message': f'✅ **Medicamento encontrado:** {medicine.name} (SKU: {medicine.sku})\n\n🔧 **Paso 2/3: Seleccionar campo**\n\n**Información actual:**\n• **SKU:** {medicine.sku}\n• **Nombre:** {medicine.name}\n• **Tipo:** {medicine.type}\n• **Precio:** S/. {medicine.price}\n• **Stock:** {medicine.stock}\n\n**¿Qué campo deseas modificar?**\n• **sku** - Código SKU\n• **name** - Nombre del medicamento\n• **type** - Tipo (pastilla, jarabe, inyectable)\n• **price** - Precio\n• **stock** - Cantidad en stock',
                'help': 'Escribe el nombre del campo que deseas modificar',
                'context_data': {
                    'identifier': identifier,
                    'medicine_sku': medicine.sku,
                    'medicine_name': medicine.name
                }
            }
        
        # Validar el campo
        valid_fields = ['sku', 'name', 'type', 'price', 'stock']
        if field not in valid_fields:
            return {
                'success': False,
                'interactive': True,
                'step': 'request_field',
                'message': f'❌ Campo inválido: "{field}"\n\n**Campos válidos:**\n• **sku** - Código SKU\n• **name** - Nombre del medicamento\n• **type** - Tipo (pastilla, jarabe, inyectable)\n• **price** - Precio\n• **stock** - Cantidad en stock\n\nPor favor, selecciona uno de estos campos.',
                'help': 'Usa uno de los campos válidos: sku, name, type, price, stock'
            }
        
        # Modo interactivo: solicitar nuevo valor
        if new_value is None:
            current_value = getattr(medicine, field)
            field_descriptions = {
                'sku': 'código SKU único',
                'name': 'nombre del medicamento',
                'type': 'tipo (pastilla, jarabe, inyectable)',
                'price': 'precio en soles (ejemplo: 15.50)',
                'stock': 'cantidad en stock (número entero)'
            }
            
            return {
                'success': False,
                'interactive': True,
                'tool': 'modify_medicine',
                'step': 'awaiting_value',
                'message': f'📝 **Paso 3/3: Nuevo valor**\n\n**Campo a modificar:** {field}\n**Valor actual:** {current_value}\n\nPor favor, proporciona el nuevo {field_descriptions[field]}.\n\n**Ejemplo:** {_get_field_example(field)}',
                'help': f'Ingresa el nuevo valor para {field}',
                'context_data': {
                    'identifier': identifier,
                    'field': field,
                    'medicine_sku': medicine.sku,
                    'medicine_name': medicine.name
                }
            }
        
        # Validaciones específicas por campo
        old_value = getattr(medicine, field)
        
        if field == 'sku':
            if Item.objects.filter(sku=new_value).exclude(id=medicine.id).exists():
                return {
                    'success': False,
                    'interactive': True,
                    'step': 'request_value',
                    'message': f'❌ Ya existe un medicamento con el SKU: "{new_value}"\n\nPor favor, proporciona un SKU diferente.',
                    'help': 'El SKU debe ser único'
                }
        elif field == 'price':
            try:
                new_value = float(new_value)
                if new_value < 0:
                    return {
                        'success': False,
                        'interactive': True,
                        'step': 'request_value',
                        'message': '❌ El precio no puede ser negativo.\n\nPor favor, ingresa un precio válido (ejemplo: 15.50).',
                        'help': 'El precio debe ser un número positivo'
                    }
            except ValueError:
                return {
                    'success': False,
                    'interactive': True,
                    'step': 'request_value',
                    'message': f'❌ "{new_value}" no es un precio válido.\n\nPor favor, ingresa un número (ejemplo: 15.50).',
                    'help': 'El precio debe ser un número válido'
                }
        elif field == 'stock':
            try:
                new_value = int(new_value)
                if new_value < 0:
                    return {
                        'success': False,
                        'interactive': True,
                        'step': 'request_value',
                        'message': '❌ El stock no puede ser negativo.\n\nPor favor, ingresa una cantidad válida (ejemplo: 100).',
                        'help': 'El stock debe ser un número entero positivo'
                    }
            except ValueError:
                return {
                    'success': False,
                    'interactive': True,
                    'step': 'request_value',
                    'message': f'❌ "{new_value}" no es una cantidad válida.\n\nPor favor, ingresa un número entero (ejemplo: 100).',
                    'help': 'El stock debe ser un número entero'
                }
        elif field == 'type':
            valid_types = ['pastilla', 'jarabe', 'inyectable']
            if new_value.lower() not in valid_types:
                return {
                    'success': False,
                    'interactive': True,
                    'step': 'request_value',
                    'message': f'❌ Tipo inválido: "{new_value}"\n\n**Tipos válidos:**\n• pastilla\n• jarabe\n• inyectable\n\nPor favor, selecciona uno de estos tipos.',
                    'help': 'Usa uno de los tipos válidos: pastilla, jarabe, inyectable'
                }
            new_value = new_value.lower()
        
        # Aplicar la modificación
        setattr(medicine, field, new_value)
        medicine.save()
        
        return {
            'success': True,
            'message': f'✅ **Medicamento modificado exitosamente**\n\n**{medicine.name}** (SKU: {medicine.sku})\n\n**Campo modificado:** {field}\n**Valor anterior:** {old_value}\n**Valor nuevo:** {new_value}',
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
            'error': f'Error al modificar medicamento: {str(e)}'
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
