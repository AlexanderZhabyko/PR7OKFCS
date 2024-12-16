from django.conf.urls.static import static
from django.urls import path

import logistic.views as v

# router = routers.SimpleRouter()
urlpatterns = [
   path('register/', v.register_view, name='register'),
   path('login/', v.login_view, name='login'),
   path('logout/', v.logout_view, name='logout'),
   path('account/', v.account_view, name='account_view'),


   path('', v.home, name='home'),
   path('logs/', v.logs_list, name='logs_list'),
   path('deliveryTime/', v.delivery_times_list, name='delivery_times_list'),
   path('orders/', v.orders_list, name='orders_list'),
   path('productOrders/', v.productorders_list, name='productorders_list'),
   path('product/', v.products_list, name='products_list'),
   path('providers/', v.providers_list, name='providers_list'),
   path('roles/', v.roles_list, name='roles_list'),
   path('stock/', v.stocks_list, name='stocks_list'),
   path('users/', v.users_list, name='users_list'),
   path('users/add/', v.add_user, name='add_user'),
   path('users/edit/<int:pk>/', v.edit_user, name='edit_user'),
   path('users/delete/<int:pk>/', v.delete_user, name='delete_user'),

   path('deliveryTime/add/', v.add_delivery_time, name='add_delivery_time'),
   path('deliveryTime/edit/<int:pk>/', v.edit_delivery_time, name='edit_delivery_time'),
   path('deliveryTime/delete/<int:pk>/', v.delete_delivery_time, name='delete_delivery_time'),

   path('orders/add/', v.add_orders, name='add_orders'),
   path('orders/edit/<int:pk>/', v.edit_orders, name='edit_orders'),
   path('orders/delete/<int:pk>/', v.delete_orders, name='delete_order'),
   path('user_order', v.user_create_order, name='user_create_order'),
   path('create_supply/', v.create_supply, name='create_supply'),


   path('productOrders/add/', v.add_productorders, name='add_productorders'),
   path('productOrders/edit/<int:pk>/', v.edit_productorders, name='edit_productorders'),
   path('productOrders/delete/<int:pk>/', v.delete_productorders, name='delete_productorders'),

   path('product/add/', v.add_product, name='add_product'),
   path('product/edit/<int:pk>/', v.edit_product, name='edit_product'),
   path('products/delete/<int:pk>/', v.delete_product, name='delete_product'),

   path('providers/add/', v.add_providers, name='add_providers'),
   path('providers/edit/<int:pk>/', v.edit_providers, name='edit_providers'),
   path('providers/delete/<int:pk>/', v.delete_provider, name='delete_provider'),


   path('roles/add/', v.add_roles, name='add_roles'),
   path('roles/edit/<int:pk>/', v.edit_roles, name='edit_roles'),
   path('roles/delete/<int:pk>/', v.delete_role, name='delete_role'),

   path('stock/add/', v.add_stock, name='add_stock'),
   path('stock/edit/<int:pk>/', v.edit_stock, name='edit_stock'),
   path('stock/delete/<int:pk>/', v.delete_stock, name='delete_stock'),

   path('order-status/', v.order_statuss_list, name='order_statuss_list'),
    path('order-status/add/', v.add_order_status, name='add_order_status'),
    path('order-status/<int:pk>/edit/', v.edit_order_status, name='edit_order_status'),
    path('order-status/<int:pk>/delete/', v.delete_order_status, name='delete_order_status'),

   path('account_delivery/', v.delivery_orders, name='delivery_orders'),

   path('mark_as_delivered/<int:order_id>/', v.mark_as_delivered, name='mark_as_delivered'),



   path('backup/', v.backup_database, name='backup_database'),
   path("restore_database/", v.restore_database, name="restore_database"),

]