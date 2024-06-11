from django.views import View
from django.views.generic import DeleteView, ListView
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pages, Products, SavedProduct, CartItem, Images, Comments
from products import forms
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Avg, Count


class HomePageView(View):
    def get(self, request):
        products = Products.objects.all().order_by('-id')
        for product in products:
            comments = Comments.objects.filter(product=product)
            product.average_rating = comments.aggregate(Avg('star_given'))['star_given__avg'] or 0
            product.average_rating = comments.count()
        context = {
            'products': products,
        }
        return render(request, 'home.html', context=context)


class SearchResultsView(ListView):
    model = Products
    template_name = 'search_results.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Products.objects.filter(
            Q(name__icontains=query) | Q(price__icontains=query)
        )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = Images.objects.filter(
            product__in=self.get_queryset()
        )
        return context


#  Page bilab bog'liq viewlar

class MypagesListView(LoginRequiredMixin, View):
    def get(self, request):
        pages = Pages.objects.filter(account=request.user)
        context = {
            'pages': pages
        }
        return render(request, 'page/my_pages.html', context=context)


class CreatePageView(LoginRequiredMixin, View):
    def get(self, request):
        create_page_form = forms.PagesForm()
        context = {
            'create_page_form': create_page_form
        }
        return render(request, 'page/create_page.html', context=context)

    def post(self, request):
        create_page_form = forms.PagesForm(request.POST, request.FILES)
        if create_page_form.is_valid():
            new_page = create_page_form.save(commit=False)
            new_page.account = request.user
            new_page.save()
            # print("New Page ID:", new_page.id)
            return redirect('products:page-detail', page_id=new_page.id)
        else:
            # print("Form Errors:", create_page_form.errors)
            context = {
                'create_page_form': create_page_form
            }
            return render(request, 'page/create_page.html', context=context)


class PageDetailView(View):
    def get(self, request, *args, **kwargs):
        page_id = kwargs.get('page_id')
        page = get_object_or_404(Pages, id=page_id)
        products = Products.objects.filter(page_id=page_id)
        context = {
            'page_id': page_id,
            'page': page,
            'products': products
        }
        return render(request, 'page/page_detail.html', context=context)


class PageUpdateView(LoginRequiredMixin, UserPassesTestMixin,  View):
    def test_func(self):
        page_id = self.kwargs['page_id']
        page = get_object_or_404(Pages, pk=page_id)
        return self.request.user == page.account

    def handle_no_permission(self):
        messages.error(self.request, "Siz bu sahifani o'zgartira olmaysiz!")
        return redirect('products:page-detail', page_id=self.kwargs['page_id'])

    def get(self, request, page_id):
        page = get_object_or_404(Pages, pk=page_id)
        form = forms.PagesForm(instance=page)
        context = {
            'form': form
        }
        return render(request, 'page/page_update.html', context=context)

    def post(self, request, page_id):
        page = get_object_or_404(Pages, pk=page_id)
        form = forms.PagesForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('products:page-detail', page_id=page_id)
        context = {
            'form': form
        }
        return render(request, 'page/page_update.html', context=context)


# Product bilan bog'liq viewlar


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        page_id = self.kwargs['page_id']
        page = get_object_or_404(Pages, pk=page_id)
        return self.request.user == page.account

    def handle_no_permission(self):
        messages.error(self.request, "Siz bu sahifada mahsulot qo'sha olmaysiz!")
        return redirect('products:page-detail', page_id=self.kwargs['page_id'])

    def get(self, request, page_id):
        create_form = forms.ProductsForm()
        image_form = forms.ProductImagesForm()
        context = {
            'create_form': create_form,
            'image_form': image_form
        }
        return render(request, 'product/product_create.html', context=context)

    def post(self, request, page_id):
        create_form = forms.ProductsForm(request.POST, request.FILES)
        image_form = forms.ProductImagesForm(request.POST, request.FILES)
        if create_form.is_valid() and image_form.is_valid():
            new_product = create_form.save(commit=False)
            page = get_object_or_404(Pages, id=page_id)
            new_product.page = page
            new_product.save()

            images = request.FILES.getlist('images')
            for image in images:
                Images.objects.create(product=new_product, image=image)

            return redirect('products:page-detail', page_id=page_id)
        else:
            context = {
                'create_form': create_form,
                'image_form': image_form
            }
            return render(request, 'product/product_create.html', context=context)


class ProductDetailView(View):
    def get(self, request, page_id, product_id, *args, **kwargs):
        page = get_object_or_404(Pages, id=page_id)
        product = get_object_or_404(Products, pk=product_id)
        productsave = SavedProduct.objects.filter(product=product)
        context = {
            'page_id': page_id,
            'product_id': product_id,
            'page': page,
            'product': product,
            'productsave': productsave,
        }
        return render(request, 'product/product_detail.html', context=context)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Products, pk=product_id)
        return self.request.user == product.page.account

    def handle_no_permission(self):
        messages.error(self.request, "Siz bu mahsulotni o'zgartira olmaysiz!")
        return redirect('products:product-detail', page_id=self.kwargs['page_id'], product_id=self.kwargs['product_id'])

    def get_object(self, pk):
        return get_object_or_404(Products, pk=pk)

    def get(self, request, page_id, product_id):
        page = get_object_or_404(Pages, id=page_id)
        product = self.get_object(product_id)
        update_form = forms.ProductsForm(instance=product)
        image_form = forms.ProductImagesForm()
        context = {
            'page_id': page_id,
            'page': page,
            'update_form': update_form,
            'image_form': image_form,
            'product': product
        }
        return render(request, 'product/product_update.html', context=context)

    def post(self, request, page_id, product_id):
        product = self.get_object(product_id)
        page = get_object_or_404(Pages, id=page_id)
        update_form = forms.ProductsForm(request.POST, request.FILES, instance=product)
        image_form = forms.ProductImagesForm(request.POST, request.FILES)

        if update_form.is_valid():
            update_form.save()

            if image_form.is_valid():
                images = request.FILES.getlist('images')
                for image in images:
                    Images.objects.create(product=product, image=image)

            return redirect('products:product-detail', page_id=page_id, product_id=product.id)
        else:
            context = {
                'page_id': page_id,
                'page': page,
                'update_form': update_form,
                'image_form': image_form,
                'product': product
            }
            return render(request, 'product/product_update.html', context=context)


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Products
    template_name = 'product/product_delete.html'
    success_url = reverse_lazy('products:home')

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.page.account

    def handle_no_permission(self):
        messages.error(self.request, "Siz bu mahsulotni o'chira olmaysiz!")
        return redirect('products:product-detail', page_id=self.kwargs['page_id'], product_id=self.kwargs['pk'])


class SavedProductView(LoginRequiredMixin, View):
    def get(self, request):
        savedproducts = SavedProduct.objects.filter(user=request.user)
        context = {
            'savedproducts': savedproducts,
        }
        return render(request, 'savedproducts.html', context=context)


@method_decorator(login_required, name='dispatch')
class SaveProductView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Products, id=product_id)
        saved_product, created = SavedProduct.objects.get_or_create(user=request.user, product=product)

        if not created:
            saved_product.delete()
            saved = False
        else:
            saved = True

        return JsonResponse({'saved': saved})


def view_cart(request,):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price_discount * item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'cart.html', context=context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    quantity = int(request.GET.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
    cart_item.quantity += quantity
    cart_item.save()

    return redirect('products:view_cart')


def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.delete()
    return redirect('products:view_cart')

# comment bilan bog'liq viewlar


class CommentCreateView(View):
    @method_decorator(login_required)
    def post(self, request, product_id):
        product = get_object_or_404(Products, id=product_id)
        form = forms.CommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = product
            comment.save()
            return redirect('products:product-detail', page_id=product.page.id, product_id=product.id)
        context = {
            'product': product,
            'form': form
        }
        return render(request, 'product/product_detail.html', context=context)


class CommentEditView(View):
    @method_decorator(login_required)
    def get(self, request, comment_id):
        comment = get_object_or_404(Comments, id=comment_id, user=request.user)
        form = forms.CommentsForm(instance=comment)
        context = {
            'form': form,
            'comment': comment,
            'product': comment.product  # Assuming comment has a 'product' field
        }
        return render(request, 'comments/edit_comment.html', context=context)

    @method_decorator(login_required)
    def post(self, request, comment_id):
        comment = get_object_or_404(Comments, id=comment_id, user=request.user)
        form = forms.CommentsForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('products:product-detail', page_id=comment.product.page.id, product_id=comment.product.id)
        context = {
            'form': form,
            'comment': comment,
            'product': comment.product
        }
        return render(request, 'comments/edit_comment.html', context=context)


class CommentDeleteView(View):
    @method_decorator(login_required)
    def get(self, request, comment_id):
        comment = get_object_or_404(Comments, id=comment_id, user=request.user)
        product = comment.product
        is_author = comment.user == request.user
        context = {
            'comment': comment,
            'product': product,
            'is_author': is_author
        }
        return render(request, 'product/delete_comment.html', context=context)

    def post(self, request, comment_id):
        comment = get_object_or_404(Comments, id=comment_id, user=request.user)
        product = comment.product
        if comment.user != request.user:
            messages.error(request, "siz bu comment egasi emasiz!")
            return redirect('products:product-detail', page_id=product.page.id, product_id=product.id)
        comment.delete()
        messages.success(request, 'comment deleted successfully')
        return redirect('products:product-detail', page_id=product.page.id, product_id=product.id)
