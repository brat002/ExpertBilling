# Create your views here.
from mikrobill.billing.models import Account, Pay
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth import logout

def index(request):
    accs=Account.objects.all()
    template_name="billing/index.html"
    #return HttpResponse(accs)
    return render_to_response(
                template_name, {
                    'accounts': accs,
                },
               )
def profile(request):
    
    if request.user.is_authenticated():
        try:
            acc=Account.objects.get(user=request.user)
            day=acc.ballance/(acc.tarif.summ/acc.tarif.period)
            template_name="accounts/index.html"
            return render_to_response(
                template_name, {
                    'account': acc,
                    'day': day,
                },
               )
        except:
            template_name="billing/index.html"
            return render_to_response(template_name)
    elif not request.user.is_authenticated():
        template_name="billing/index.html"
        return render_to_response(template_name)

            

               
def logout_view(request):
    logout(request)
    template_name="accounts/succeful.html"
    return render_to_response(template_name)
    # Redirect to a success page.