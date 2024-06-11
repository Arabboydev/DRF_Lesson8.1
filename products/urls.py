from django.urls import path
from products import views

app_name = 'products'

urlpatterns = [
    # home page
    path('', views.HomePageView.as_view(), name='home'),
    # create new page
    path('page/create/', views.CreatePageView.as_view(), name='create-page'),
    # view cart
    path('cart/', views.view_cart, name='view_cart'),
    # add to cart url
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # remove from cart url
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # page urls
    path('page/<int:page_id>/detail/', views.PageDetailView.as_view(), name='page-detail'),
    path('page/<int:page_id>/edit/', views.PageUpdateView.as_view(), name='page-edit'),
    path('page/mine/', views.MypagesListView.as_view(), name='page-mine'),
    # products urls
    path('page/<int:page_id>/product/<int:product_id>/detail/', views.ProductDetailView.as_view(), name='product-detail'),
    path('page/<int:page_id>/product/<int:product_id>/edit/', views.ProductUpdateView.as_view(), name='product-update'),
    path('page/<int:page_id>/product/create/', views.ProductCreateView.as_view(), name='product-create'),
    # search bar url
    path('search-results/', views.SearchResultsView.as_view(), name='search-results'),
    # saved page url
    path('product/<int:product_id>/save/', views.SaveProductView.as_view(), name='save_product'),
    path('saved/products/', views.SavedProductView.as_view(), name='saved-products'),
    # comment urls
    path('product/<int:product_id>/comment/add/', views.CommentCreateView.as_view(), name='add-comment'),
    path('comment/<int:comment_id>/edit/', views.CommentEditView.as_view(), name='edit-comment'),
    path('comment/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='delete-comment'),
]
