#coding=utf-8
from django.shortcuts import render, get_object_or_404
import markdown
# Create your views here.
from comments.forms import CommentForm
from django.http import HttpResponse
from .models import Post, Category, Tag
from django.views.generic import ListView, DetailView
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.db.models import Q


class IndexView(ListView):
    # 将model指定为Post，告诉Django我要获取的是Post
    model = Post
    # 指定这个视图渲染的模板
    template_name = 'blog/index.html'
    # 指定获取的模型列表数据保存的变量名，这个变量会被传递给模板
    context_object_name = 'post_list'
    paginate_by = 3


    def get_context_data(self, **kwargs):
        # 覆写该方法，以便我们获得自定义的模板变量

        context = super(IndexView,self).get_context_data(**kwargs)

        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        # 例如如果规定每页 10 个数据，而本身只有 5 个数据，其实就用不着分页，此时 is_paginated=False。
        # 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        pagination_data = self.pagination_data(paginator, page, is_paginated)
        context.update(pagination_data)
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}

        left = []
        right = []

        left_has_more = False
        right_has_more = False
        first = False
        last = False

        page_number = page.number
        total_pages = paginator.num_pages

        #获得整个分页的页码列表
        page_range = list(paginator.page_range)

        if page_number ==1:
#            right = page_range[page_number:page_number + 1]
            right = page_range[page_number:page_number + 1]

            if right[-1] < total_pages -1:
                right_has_more = True

            if right[-1] <total_pages:
                last = True
        elif page_number ==total_pages:
            left = page_range[(page_number - 3) if (page_number -3) > 0 else 0 :page_number -1]

            if left[0] > 2:
                left_has_more =True
            if left[0] >1:
                first = True

        else:
            left = page_range[(page_number - 3) if(page_number-3) >0 else 0: page_number -1]
            right = page_range[page_number:page_number + 1]

            if right[-1] < total_pages -1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            if left[0] >2:
                left_has_more = True
            if left[0] >1:
                first = True


        data = {
            'left':left,
            'right':right,
            'left_has_more':left_has_more,
            'right_has_more':right_has_more,
            'last':last,
            'first': first,
        }

        return data


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆盖父类get方法
        # 父类get方法返回一个Httpresponse实例，
        # 之所以调用父类get方法，是因为只有当get方法被调用后，才有self.object属性，其值为Post模型实例
        response = super(PostDetailView,self).get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_object(self, queryset=None):
        # 覆盖父类get_object方法

        post = super(PostDetailView,self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            #   'markdown.extensions.toc',
            TocExtension(slugify=slugify),
            ])


        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):
        # 覆盖get_context_data 的目的是为了除了将post传递给模板外（DateilView已经帮我们完成）
        # 还要把评论表单、post下评论的列表传递给模板
        context = super(PostDetailView,self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update(
            {
                'form':form,
                'comment_list':comment_list
            }
        )
        return context


class In_TimeView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(In_TimeView,self).get_queryset().filter(created_time__year=year, created_time__month=month)

class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


class Tag_CloudView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tg = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(Tag_CloudView, self).get_queryset().filter(tags=tg)



def search(request):
    q = request.GET.get('q')
    error_msg = ''
    if not q:
        error_msg = "请输入关键词"
        return render(request,'blog/index.html',{'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {'error_msg': error_msg, 'post_list': post_list })