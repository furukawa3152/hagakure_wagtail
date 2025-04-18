from django import forms
from django.db import models

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.search import index

from wagtail.admin.panels import FieldPanel, InlinePanel,  MultiFieldPanel
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from django.db.models import Q
from wagtail.snippets.models import register_snippet
from wagtailmarkdown.blocks import MarkdownBlock
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# チャンネルのための追加
@register_snippet
class BlogChannel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ブログチャンネル"
        verbose_name_plural = "ブログチャンネル"

# タグインデックスのための追加
class BlogTagIndexPage(Page):

    def get_context(self, request):
        tag_param = request.GET.get('tag', '').strip()
        tag_list = tag_param.split()
        tag_query = Q()
        for tag in tag_list:
            tag_query |= Q(tags__slug=tag)  # ← name から slug に変更

        blogpages = BlogPage.objects.filter(tag_query).distinct()

        context = super().get_context(request)
        context['blogpages'] = blogpages
        context['search_tags'] = tag_list
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )

# いいねボタンの実装
class Like(models.Model):
    blogpage = models.ForeignKey('BlogPage', verbose_name='ブログ記事', on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["blogpage", "ip_address"],
                name="like_unique"
            ),
        ]
# ------いいねボタンここまで


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

class BlogIndexPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        query = request.GET.get('q', '').strip()

        if query:
            tags = query.split()
            blogpages = BlogPage.objects.filter(Q(tags__name__in=tags)).distinct()
        else:
            blogpages = BlogPage.objects.all()

        # 公開済み & 新しい順に
        blogpages = blogpages.live().order_by('-first_published_at')

        # ✅ ページネーション追加（12件/ページ）
        paginator = Paginator(blogpages, 12)
        page = request.GET.get('page')

        try:
            blogpages_page = paginator.page(page)
        except PageNotAnInteger:
            blogpages_page = paginator.page(1)
        except EmptyPage:
            blogpages_page = paginator.page(paginator.num_pages)

        context['blogpages'] = blogpages_page
        context['search_query'] = query
        return context

    

class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('rich_text', blocks.RichTextBlock(
            features=['h2', 'h3', 'bold', 'italic', 'ol', 'ul', 'embed', 'image', 'link', 'document-link', 'code', 'blockquote'],
            blank=True,
            label='テキスト')),
        ('markdown', MarkdownBlock(blank=True, label='マークダウン')),
    ])

    # チャンネル
    channel = models.ForeignKey(
        'BlogChannel',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )


    # タグ
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    primary_tag = models.ForeignKey('taggit.Tag', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    # ... Keep the main_image method and search_fields definition. Then modify the content_panels:
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("date"),
            FieldPanel('channel'),
            FieldPanel("tags"),
        ], heading="Blog information"),
        FieldPanel("intro"),
        FieldPanel("body"),
        "gallery_images",
    ]

    # いいねボタンの実装

    def get_like_count(self):
        return self.like_set.aggregate(total_likes=models.Sum('count'))['total_likes'] or 0

    def is_liked_by(self, user):
        return self.like_set.filter(user=user).exists()

    # ------いいねボタンここまで
    #
    def get_first_gallery_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = ["image", "caption"]

