ade25.banner
============

Plone banner management and carousel implementation

Rationale
---------

This addon provides a dexterity banner content type that is for simplicity
reasons globally addable. A bahavior is provided that can be activated on
folderish content types to display a banner viewlet in the portal footer.

Note: In order to make the plone site aka the front page display banner
content, you need to set the corresponding marker interface via the ZMI.


Hint:
-----

The package provides a helper view to set this marker interface on the site
root for you callable via '${portal_ul}/@@enable-site-banners'.
