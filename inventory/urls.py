from django.urls import path
from .views import item_list, mcp_tool_use, dashboard, chatbot_endpoint, ChatbotIntelligentView

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('inventory/', item_list, name='item-list'),
    path('dashboard/', dashboard, name='dashboard-alt'),
    path('chatbot_api/', chatbot_endpoint, name='chatbot_api'),
    path('chatbot_smart/', ChatbotIntelligentView.as_view(), name='chatbot_smart'),
    path('mcp/tool_use/', mcp_tool_use, name='mcp_tool_use'),
]