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


def item_list(request):
    items = Item.objects.all()
    return render(request, 'inventory/item_list.html', {'items': items})

def dashboard(request):
    items = Item.objects.all()
    return render(request, 'inventory/dashboard.html', {'items': items})

def normalize_text(text):
    if not text:
        return ""
    

    text = text.lower()
    

    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    

    return text.strip()

def recognize_intent(message):
    normalized_message = normalize_text(message)
    
    if any(word in normalized_message for word in ['eliminar', 'borrar', 'quitar', 'remover', 'delete']):
        if any(word in normalized_message for word in ['medicamento', 'medicina', 'producto']):
            return 'delete_medicine'
    
    if any(word in normalized_message for word in ['modificar', 'editar', 'alterar', 'cambiar', 'actualizar']):
        if any(word in normalized_message for word in ['medicamento', 'medicina', 'producto']):
            return 'modify_medicine'
    
    if any(word in normalized_message for word in ['crear', 'nuevo', 'agregar', 'añadir', 'crea', 'registrar']):
        if any(word in normalized_message for word in ['medicamento', 'medicina', 'producto']) or 'nuevo' in normalized_message:
            return 'create_medicine'
    
    if any(word in normalized_message for word in ['obtener', 'ver', 'mostrar', 'buscar', 'consultar', 'sku', 'informacion', 'info']):
        return 'get_item'
    
    return None

def get_help_message():
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
    try:
    
        data = json.loads(request.body)
        tool_name = data.get('tool_name')
        parameters = data.get('parameters', {})
        
    
        if not tool_name:
            return JsonResponse({
                'success': False,
                'error': 'Se requiere especificar tool_name'
            }, status=400)
        
        available_tools = {
            'create_medicine': create_medicine_tool,
            'get_item': get_item_tool,
            'delete_medicine': delete_medicine_tool,
            'modify_medicine': modify_medicine_tool
        }
        
    
        if tool_name not in available_tools:
            return JsonResponse({
                'success': False,
                'error': f'Herramienta {tool_name} no disponible. Herramientas disponibles: {", ".join(available_tools.keys())}'
            }, status=400)
        
    
        tool_function = available_tools[tool_name]
        
    
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
            
        elif tool_name == 'get_item':
            sku = parameters.get('sku')
            
            if not sku:
                return JsonResponse({
                    'success': False,
                    'error': 'Se requiere el parámetro sku'
                }, status=400)
            
            result = tool_function(sku)
            
        elif tool_name == 'delete_medicine':
            identifier = parameters.get('identifier')
            
            if not identifier:
                return JsonResponse({
                    'success': False,
                    'error': 'Se requiere el parámetro identifier'
                }, status=400)
            
            result = tool_function(identifier)
            
        elif tool_name == 'modify_medicine':
            identifier = parameters.get('identifier')
            field = parameters.get('field')
            new_value = parameters.get('new_value')
            step = parameters.get('step')
            
            result = tool_function(identifier, field, new_value, step)
        
    
        if isinstance(result, dict) and 'success' in result:
            return JsonResponse(result)
        else:
    
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
    try:
    
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        context = data.get('context', None)
        
    
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Se requiere proporcionar un mensaje'
            }, status=400)
        
    
        request.session.setdefault('chatbot_state', {'action': None, 'data': {}})
        chatbot_state = request.session['chatbot_state']
        
    
        current_action = chatbot_state.get('action')
        
    
        escape_commands = ['cancelar', 'cancel', 'salir', 'exit', 'terminar', 'olvidar', 'empezar de nuevo', 'reiniciar', 'reset', 'nuevo']
        if normalize_text(message) in escape_commands:
    
            request.session['chatbot_state'] = {'action': None, 'data': {}}
            return JsonResponse({
                'success': True,
                'message': 'Ok, he olvidado la conversación actual. ¿En qué puedo ayudarte ahora?',
                'help': 'Puedes crear, modificar o eliminar medicamentos.'
            })
        
    
        new_intent = recognize_intent(message)
        if new_intent and current_action:
    
            clear_intents = ['create_medicine', 'delete_medicine', 'modify_medicine']
            if new_intent in clear_intents:

                request.session['chatbot_state'] = {'action': None, 'data': {}}
                current_action = None
        

        if current_action == 'esperando_sku_modificar':

            result = get_item_tool(message)
            if result.get('success'):

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

            valid_fields = ['nombre', 'name', 'tipo', 'type', 'categoria', 'category', 'precio', 'price', 'stock']
            field_normalized = normalize_text(message)
            
            
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

            identifier = chatbot_state['data'].get('identifier')
            field = chatbot_state['data'].get('field')
            
            
            result = modify_medicine_tool(identifier=identifier, field=field, new_value=message, step='complete')
            
            
            request.session['chatbot_state'] = {'action': None, 'data': {}}
            
            return JsonResponse(result)
        

        intent = new_intent if new_intent else recognize_intent(message)
        

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
        

        available_tools = {
            'create_medicine': create_medicine_tool,
            'get_item': get_item_tool,
            'delete_medicine': delete_medicine_tool,
            'modify_medicine': modify_medicine_tool
        }
        

        if intent == 'create_medicine':

            

            normalized_message = normalize_text(message)
            

            name_match = re.search(r'medicamento\s+(\w+)', normalized_message)
            type_match = re.search(r'tipo\s+(\w+)', normalized_message)
            category_match = re.search(r'categoria\s+(\w+)', normalized_message)
            price_match = re.search(r'precio\s+([\d.]+)', normalized_message)
            stock_match = re.search(r'stock\s+(\d+)', normalized_message)
            
            if all([name_match, type_match, category_match, price_match, stock_match]):
    
                try:
                    name = name_match.group(1)
                    medicine_type = type_match.group(1)
                    disease_category = category_match.group(1)
                    price = float(price_match.group(1))
                    stock = int(stock_match.group(1))
                    
    
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

            sku_pattern = r'SKU-?(\d+)'
            sku_match = re.search(sku_pattern, message.upper())
            
            if sku_match:
                sku_id = sku_match.group(1)
                sku = f'SKU-{sku_id}'
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

            sku_match = re.search(r'SKU-?(\d+)', message.upper())
            if sku_match:
                sku_id = sku_match.group(1)
                sku = f'SKU-{sku_id}'
                result = available_tools[intent](sku)
                return JsonResponse(result)
            else:


                words = message.lower().split()
                stop_words = {'eliminar', 'medicamento', 'medicina', 'producto', 'el', 'la', 'un', 'una', 'de', 'del'}
                medicine_words = [word for word in words if word not in stop_words and len(word) > 2]
                
                if medicine_words:
    
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
    try:
    
        data = json.loads(request.body)
        tool_name = data.get('tool_name')
        parameters = data.get('parameters', {})
        
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
            
        
            result = create_medicine_tool(name, medicine_type, disease_category, price, stock)
            return JsonResponse(result)
        

        
        elif tool_name == 'get_item':
        
            sku = parameters.get('sku')
            
        
            if not sku:
                return JsonResponse({
                    'success': False,
                    'error': 'El parámetro sku es requerido'
                }, status=400)
            
        
            result = get_item_tool(sku)
            return JsonResponse(result)
        

        
        elif tool_name == 'delete_medicine':
        
            sku = parameters.get('sku')
            
        
            if not sku:
                return JsonResponse({
                    'success': False,
                    'error': 'El parámetro sku es requerido'
                }, status=400)
            
        
            result = delete_medicine_tool(sku)
            return JsonResponse(result)
        
        elif tool_name == 'modify_medicine':
    
            identifier = parameters.get('identifier')
            field = parameters.get('field')
            new_value = parameters.get('new_value')
            step = parameters.get('step')
            
    
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

    load_dotenv()
    

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return {
            'success': False,
            'error': 'GEMINI_API_KEY no encontrada en las variables de entorno'
        }
    

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    

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
    
        response = model.generate_content(prompt)
        
    
        response_text = response.text.strip()
        
    
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            return {
                'success': False,
                'error': f'No se encontró JSON válido en la respuesta de Gemini: {response_text}'
            }
        
        json_str = response_text[start_idx:end_idx]
        
    
        medicine_data = json.loads(json_str)
        

        import uuid
        sku = f"MED-{str(uuid.uuid4())[:8].upper()}"
        

        new_item = Item(
            sku=sku,
            name=medicine_data['name'],
            type=medicine_data['type'],
            disease_category=medicine_data['disease_category'],
            price=float(medicine_data['price']),
            stock=int(medicine_data['stock'])
        )
        

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




def get_item_tool(sku):
    try:
    
        try:
            item = Item.objects.get(sku=sku)
        except Item.DoesNotExist:
            return {
                'success': False,
                'error': f'Medicamento con SKU {sku} no encontrado'
            }
        
    
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



def delete_medicine_tool(identifier):
    try:
    
        item = None
        

        try:
            item = Item.objects.get(sku=identifier)
        except Item.DoesNotExist:
    
            try:
                item = Item.objects.get(name__iexact=identifier)
            except Item.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Medicamento con SKU o nombre "{identifier}" no encontrado'
                }
        

        order_lines = OrderLine.objects.filter(item=item)
        if order_lines.exists():
            return {
                'success': False,
                'error': f'No se puede eliminar el medicamento {item.name} (SKU: {item.sku or "N/A"}) porque tiene órdenes asociadas. Primero debe revertir las órdenes relacionadas.'
            }
        

        medicine_name = item.name
        medicine_sku = item.sku or "N/A"
        

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
    try:
    
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
        

        medicine = None
        try:
            medicine = Item.objects.get(sku=identifier)
        except Item.DoesNotExist:
            try:
                medicine = Item.objects.get(name__iexact=identifier)
            except Item.DoesNotExist:
    
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
        

        valid_fields = ['sku', 'name', 'type', 'price', 'stock']
        if field not in valid_fields:
            return {
                'success': False,
                'interactive': True,
                'step': 'request_field',
                'message': f'❌ Campo inválido: "{field}"\n\n**Campos válidos:**\n• **sku** - Código SKU\n• **name** - Nombre del medicamento\n• **type** - Tipo (pastilla, jarabe, inyectable)\n• **price** - Precio\n• **stock** - Cantidad en stock\n\nPor favor, selecciona uno de estos campos.',
                'help': 'Usa uno de los campos válidos: sku, name, type, price, stock'
            }
        
    
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
    examples = {
        'sku': 'MED001',
        'name': 'Aspirina 500mg',
        'type': 'pastilla',
        'price': '15.50',
        'stock': '100'
    }
    return examples.get(field, 'valor')
