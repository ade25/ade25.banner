from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from zope import schema
from zope.schema import getFieldsInOrder
from zope.component import getUtility

from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button

from plone.namedfile.field import NamedBlobImage
from plone.app.textfield import RichText

from plone.dexterity.interfaces import IDexterityFTI
from Products.statusmessages.interfaces import IStatusMessage

from ade25.banner.contentbanner import IContentBanner

from ade25.banner import MessageFactory as _


class IContentBannerEdit(form.Schema):

    headline = schema.TextLine(
        title=_(u"Banner Headline"),
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


class IContentBannerImageEdit(form.Schema):

    image = NamedBlobImage(
        title=_(u"Image"),
        required=False,
    )


class ContentBannerEditForm(form.SchemaEditForm):
    grok.context(IContentBanner)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-banner')

    schema = IContentBannerEdit
    ignoreContext = False
    css_class = 'app-form'

    label = _(u"Edit content panel")

    def updateActions(self):
        super(ContentBannerEditForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary btn-editpanel")
        self.actions['cancel'].addClass("btn btn-default")

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Content block factory has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.banner.contentbanner')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.banner.contentbanner')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The banner has successfully been updated"),
            type='info')
        parent = aq_parent(context)
        next_url = parent.absolute_url()
        return self.request.response.redirect(next_url)


class ContentBannerImageEditForm(form.SchemaEditForm):
    grok.context(IContentBanner)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-banner-image')

    schema = IContentBannerImageEdit
    ignoreContext = False
    css_class = 'app-form'

    label = _(u"Edit banner background image")

    def updateActions(self):
        super(ContentBannerImageEditForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary btn-editpanel")
        self.actions['cancel'].addClass("btn btn-default")

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        IStatusMessage(self.request).addStatusMessage(
            _(u"The process has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.banner.contentbanner')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='ade25.banner.contentbanner')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The banner has successfully been updated"),
            type='info')
        parent = aq_parent(context)
        next_url = parent.absolute_url()
        return self.request.response.redirect(next_url)
