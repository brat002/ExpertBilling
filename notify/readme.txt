=============
Django Notify
=============

Provides a temporary (i.e. usually until the next request which retrieves them)
notification list.


Installation
============

Add the following line to your ``MIDDLEWARE_CLASSES`` setting::

    'django_notify.middleware.NotificationsMiddleware',

The default temporary storage uses sessions, so it is best to place this after
the ``SessionMiddleware``.

You can also install the context processor into your
``TEMPLATE_CONTEXT_PROCESSORS`` setting::

    'django_notify.context_processors.notifications',


Usage
=====

Adding a temporary notification message
---------------------------------------

The middleware adds an instance of a temporary storage class called
``notifications`` to your ``request``. To add a notification, call::

    request.notifications.add('Hello world.')

You can optionally provide a string containing tags (which is usually
represented as HTML classes for the message)::

    request.notifications.add('Your rating is over 9000!', 'error')

Displaying temporary notifications
-----------------------------------

In your template (rendered with RequestContext or with
``request.notifications`` passed as ``notifications`` in its context) using
something like::

	{% if notifications %}
	<ul class="notifications">
		{% for message in notifications %}
		<li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
		{% endfor %}
	</ul>
	{% endif %}

The notifications are marked to be cleared when the storage instance is
iterated (cleared when the response is processed). To avoid the notifications
being cleared, you can set ``request.notifications.used = False`` after
iterating.


Temporary Storage
=================

Django notify can use different types of temporary storage. To change which
storage is being used, add a ``NOTIFICATIONS_STORAGE`` to your settings,
referencing to the module and class of the storage class. For example::

    NOTIFICATIONS_STORAGE = 'cookie.CookieStorage'

Django Notify first looks for the module inside of ``django_notify.storage``,
and if not found, tries to import the full given module directly.

Two temporary storage classes are included in Django Notify:

``'session.SessionStorage'``
    This is the default storage. It relies on Django's session.

``'cookie.CookieStorage'``
    This method stores the notification data in a cookie (signed with a secret
    hash to prevent manipulation) to persist notifications across requests.

To write your own, subclass the ``BaseStorage`` class in
``django_notify.storage.base`` and write ``get`` and ``store`` methods.
