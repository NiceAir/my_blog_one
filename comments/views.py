#coding=utf-8
from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post
from models import Comment
from forms import CommentForm

# Create your views here.

def post_comment(request, post_pk):

    #当获取的文章（Post）存在时，则获取；不存在，返回404页面
    post = get_object_or_404(Post, pk = post_pk)

    if request.method == 'POST':

        #利用用户提交的数据构造CommentForm实例
        form  = CommentForm(request.POST)
        if form.is_valid():

            #commit=False 的作用仅仅是利用表单的数据生成Comment模型类的实例，
            #但是还没保存数据到数据库
            comment = form.save(commit=False)

            #将评论与被评论文章关联
            comment.post = post
            comment.save()

            #重定向到post详情页，实际上当redirect函数接收一个模型的实例时，
            #它会调用这个模型实例的get_absolute_url方法，
            #然后重定向到get_absolute_url返回的url
            return redirect(post)
        else:
            #检查到数据不合法，重新渲染详情页，并且渲染表单的错误
            # post.comment_set.all() 方法类似于 Post.objects.all() ，
            #作用是获取当前文章下全部的评论。
            #因为 Post 和 Comment 是用外键关联的，所以可以用post.comment_set.all()反向查询全部评论
            comment_list = post.comment_set.all()
            context = {'post':post, 'form':form, 'comment_list':comment_list}
            return render(request,'blog/detail.html', context=context)
    return redirect(post)
