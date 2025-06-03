from django.urls import path
from .views import create_product_user_detail,order_summary_view,delete_product_view,edit_product_user_detail,export_user_product_details_xls


urlpatterns = [
    path('', create_product_user_detail, name='create-product-user'),
    path('order-summery/', order_summary_view, name='order_summary_view'),
    path('product-delete/<int:product_id>/', delete_product_view, name='delete_product'),
    path('product-user-detail/edit/<int:pk>/', edit_product_user_detail, name='edit_product_user_detail'),
    path('export-user-products/', export_user_product_details_xls, name='export_user_products'),

]