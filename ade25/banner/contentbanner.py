# -*- coding: utf-8 -*-
"""Module providing content banners"""
from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.textfield import RichText
from plone.app.z3cform.widget import LinkFieldWidget
from plone.app.z3cform.utils import replace_link_variables_by_paths
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.uuid.interfaces import IUUID
from Products.Five.utilities.marker import mark
from zope import schema
from zope.component import getMultiAdapter

from ade25.banner.interfaces import IBannerEnabled

from ade25.banner import MessageFactory as _

IMG = 'data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs='
BG = 'background:url({0}) no-repeat 50% 0 transparent;'


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
    form.widget(link=LinkFieldWidget)
    link = schema.TextLine(
        title=_(u"Link"),
        description=_(u"Optional internal or external link that will be "
                      u"applied to the banner automatically"),
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
        if (context.headline or context.text or context.Description()):
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

    def update(self):
        self.show_gallery = len(self.parent_banners()) > 1

    def banner_background(self):
        img = self.getImageTag()
        alt = BG.format(img)
        # style = 'background: transparent'
        style = alt
        if self.is_first_banner():
            style = alt
        return style

    def is_first_banner(self):
        context = aq_inner(self.context)
        first_item = self.parent_banners()[0]
        primary = False
        if first_item.uuid() == IUUID(context):
            primary = True
        return primary

    def has_data(self):
        context = aq_inner(self.context)
        has_content = False
        if (context.headline or context.text or context.Description()):
            has_content = True
        return has_content

    def has_link_action(self):
        context = aq_inner(self.context)
        if context.link:
            return True
        return False

    def get_link_action(self):
        context = aq_inner(self.context)
        link = context.link
        link_action = replace_link_variables_by_paths(context, link)
        return link_action

    def banner_position(self):
        context = aq_inner(self.context)
        counter = 0
        for item in self.parent_banners():
            counter += 1
            if item.uuid() == IUUID(context):
                return counter

    def parent_banners(self):
        context = aq_inner(self.context)
        asignment_context = aq_parent(context)
        if INavigationRoot.providedBy(context):
            asignment_context = context
        items = asignment_context.restrictedTraverse('@@folderListing')(
            portal_type='ade25.banner.contentbanner',
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
        else:
            image_tag = IMG
        return image_tag


class TransitionState(grok.View):
    grok.context(IContentBanner)
    grok.require('cmf.ModifyPortalContent')
    grok.name('transition-state')

    def render(self):
        context = aq_inner(self.context)
        uuid = self.request.get('uuid', '')
        state = api.content.get_state(obj=context)
        if state == 'published':
            api.content.transition(obj=context, transition='retract')
        else:
            api.content.transition(obj=context, transition='publish')
        came_from = api.content.get(UID=uuid)
        next_url = came_from.absolute_url()
        return self.request.response.redirect(next_url)


class EnableSiteBanners(grok.View):
    grok.context(INavigationRoot)
    grok.require('cmf.ManagePortal')
    grok.name('enable-site-banners')

    def render(self):
        portal = api.portal.get()
        mark(portal, IBannerEnabled)
        return self.request.response.redirect(portal.absolute_url())
