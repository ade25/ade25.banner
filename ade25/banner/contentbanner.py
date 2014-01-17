from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from plone import api
from zope.component import getMultiAdapter

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Item

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.uuid.interfaces import IUUID

from atix.sitecontent import MessageFactory as _


class IContentBanner(form.Schema, IImageScaleTraversable):
    """
    A banner acting as a page header
    """
    title = schema.TextLine(
        title=_(u"Content panel title"),
        required=True,
    )
    headline = schema.TextLine(
        title=_(u"Content Block Headline"),
        description=_(u"Optional headline for this block"),
        required=False,
    )
    description = schema.Text(
        title=_(u"Teaser"),
        description=_(u"Short and visualy highlighted teaser message"),
        required=False,
    )
    text = RichText(
        title=_(u"Block Body Text"),
        required=False,
    )
    image = NamedBlobImage(
        title=_(u"Image"),
        required=False,
    )


class ContentBanner(Item):
    grok.implements(IContentBanner)
    pass


class View(grok.View):
    grok.context(IContentBanner)
    grok.require('zope2.View')
    grok.name('view')

    def render_item(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@content-view')()
        return template


class ContentView(grok.View):
    grok.context(IContentBanner)
    grok.require('zope2.View')
    grok.name('content-view')

    def asignment_context(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        return parent.absolute_url()

    def is_editable(self):
        return not api.user.is_anonymous()

    def has_data(self):
        context = aq_inner(self.context)
        has_content = False
        if (context.headline or context.Description()):
            has_content = True
        return has_content

    def computed_klass(self):
        klass = 'app-contentblock-default'
        if not api.user.is_anonymous():
            state = self.item_state_info()
            state_klass = ('app-contentbanner-{0}').format(state)
            klass = state_klass + ' app-contentbanner-editable'
        return klass

    def item_state_info(self):
        context = aq_inner(self.context)
        return api.content.get_state(obj=context)

    def render_item(self):
        context = aq_inner(self.context)
        template = context.restrictedTraverse('@@banner-view')()
        return template


class BannerView(grok.View):
    grok.context(IContentBanner)
    grok.require('zope2.View')
    grok.name('banner-view')

    def banner_background(self):
        img_tag = self.getImageTag()
        style = 'background:url({0}) no-repeat 50% 0 transparent;'.format(
            img_tag)
        return style

    def is_first_banner(self):
        context = aq_inner(self.context)
        first_item = self.parent_banners()[0]
        primary = False
        if first_item.uuid() == IUUID(context):
            primary = True
        return primary

    def banner_position(self):
        context = aq_inner(self.context)
        counter = 0
        for item in self.parent_banners():
            counter += 1
            if item.uuid() == IUUID(context):
                return counter

    def parent_banners(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        items = parent.restrictedTraverse('@@folderListing')(
            portal_type='atix.sitecontent.contentbanner',
            sort_on='getObjPositionInParent')
        return items

    def asignment_context(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        return parent.absolute_url()

    def getImageTag(self):
        context = aq_inner(self.context)
        scales = getMultiAdapter((context, self.request), name='images')
        scale = scales.scale('image')
        if scale is not None:
            image_tag = scale.url
        return image_tag
