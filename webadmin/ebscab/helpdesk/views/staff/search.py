# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from helpdesk.lib import staff_member_required
from helpdesk.models import SavedSearch


@staff_member_required
def save_query(request):
    title = request.POST.get('title', None)
    shared = request.POST.get('shared', False)
    query_encoded = request.POST.get('query_encoded', None)

    if not title or not query_encoded:
        return HttpResponseRedirect(reverse('helpdesk_list'))

    query = SavedSearch(title=title, shared=shared,
                        query=query_encoded, user=request.user)
    query.save()

    return HttpResponseRedirect('%s?saved_query=%s' %
                                (reverse('helpdesk_list'), query.id))


@staff_member_required
def delete_saved_query(request, id):
    query = get_object_or_404(SavedSearch, id=id, user=request.user)

    if request.method == 'POST':
        query.delete()
        return HttpResponseRedirect(reverse('helpdesk_list'))
    else:
        return render(request,
                      'helpdesk/confirm_delete_saved_query.html',
                      {'query': query})
