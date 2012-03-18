from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.template.context import RequestContext
from django.db.models.query_utils import Q
from django.shortcuts import render_to_response, get_object_or_404

from object_log.models import LogItem


def list_for_object(request, obj, rest=False):
    """
    Lists all actions that involve a given object.  This will check
    LogItem.object1, LogItem.object2, and LogItem.object3.

    This view does not
    include any permission checks as it is intend

    @param request: http request
    @param obj: object to retrieve log items for
    """
    content_type = ContentType.objects.get_for_model(obj)

    q = Q(object_type1=content_type, object_id1=obj.pk) \
        | Q(object_type2=content_type, object_id2=obj.pk) \
        | Q(object_type3=content_type, object_id3=obj.pk) \

    log = LogItem.objects.filter(q).select_related('user').distinct()

    if not rest:
        return render_to_response('object_log/log.html',
            {'log':log,
             'context':{'user':request.user}
             },
            context_instance=RequestContext(request))
    else:
        return log


@login_required
def list_for_user(request, pk, rest=False):
    """
    Provided view for listing actions performed on a user.

    This may only be used by superusers
    """
    if not request.user.is_superuser:
        if not rest:
            return HttpResponseForbidden('You are not authorized to view this page')
        else:
            return {'error':'You are not authorized to view this page'}

    user = get_object_or_404(User, pk=pk)
    return list_for_object(request, user, rest)


@login_required
def list_for_group(request, pk, rest=False):
    """
    Provided view for listing actions performed on a group.

    This may only be used by superusers
    """
    if not request.user.is_superuser:
        if not rest:
            return HttpResponseForbidden('You are not authorized to view this page')
        else:
            return {'error':'You are not authorized to view this page'}

    group = get_object_or_404(Group, pk=pk)

    return list_for_object(request, group, rest)



@login_required
def list_user_actions(request, pk, rest=False):
    """
    List all actions a user has performed.  This view can only be used by
    superusers.

    @param request: HttpRequest
    @param pk: Primary Key of User to get log for.
    """
    if not request.user.is_superuser:
        if not rest:
            return HttpResponseForbidden('You are not authorized to view this page')
        else:
            return {'error':'You are not authorized to view this page'}

    user = get_object_or_404(User, pk=pk)
    log_items = LogItem.objects.filter(user=user).select_related('user')

    if not rest:
        return render_to_response('object_log/log.html',
            {'log':log_items, 'context':{'user':request.user}},
            context_instance=RequestContext(request))
    else:
        return log_items


def object_detail(request, content_type_id, pk):
    """
    Generic view for displaying a detail page for an object.  ContentTypes are
    used to find a detail url through get_absolute_url().  This isn't the most
    efficient way to display a detail page, but it will scale well with log
    messages that might not have the full item loaded.
    """
    ct = ContentType.objects.get(pk=content_type_id)
    obj = ct.get_object_for_this_type(pk=pk)
    return HttpResponseRedirect(obj.get_absolute_url())