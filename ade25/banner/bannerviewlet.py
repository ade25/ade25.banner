from Acquisition import aq_inner, aq_parent
from five import grok
from plone import api

from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.uuid.interfaces import IUUID

from ade25.banner.interfaces import IBannerEnabled
from ade25.banner.contentbanner import IContentBanner


class BannerViewlet(grok.Viewlet):
    grok.context(IBannerEnabled)
    grok.viewletmanager(IPortalFooter)
    grok.require('zope2.View')
    grok.name('ade25.banner.PageBannerViewlet')

    def update(self):
        self.has_banners = len(self.banners()) > 0
        self.show_carousel = len(self.banners()) > 1

    def static_banner(self):
        items = self.banners()
        first_item = items[0].getObject()
        return IUUID(first_item, None)

    def render_item(self, uid):
        item = api.content.get(UID=uid)
        template = item.restrictedTraverse('@@banner-view')()
        return template

    def banners(self):
        context = aq_inner(self.context)
        assignment_context = aq_parent(context)
        if INavigationRoot.providedBy(context):
            assignment_context = context
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IContentBanner.__identifier__,
                        path=dict(query='/'.join(
                                    assignment_context.getPhysicalPath()
                                    ),
                                  depth=1),
                        review_state='published',
                        sort_on='getObjPositionInParent')
        return items
