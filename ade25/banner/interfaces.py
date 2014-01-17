from zope.interface import Interface


class IBannerEnabled(Interface):
    """ Marker interface for banner enabled content """


class INavRootBannerEnabled(IBannerEnabled):
    """ Marker interface to enable navroot banner viewlet display """
