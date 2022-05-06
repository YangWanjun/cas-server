import base64
import urllib.parse

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from mama_cas.models import ServiceTicket
from mama_cas.utils import redirect as cas_redirect

User.add_to_class(
    "__str__",
    lambda x: '{}{}{}'.format(
        x.last_name,
        (' ' if x.last_name or x.first_name else ''),
        x.first_name
    ) if x.last_name or x.first_name else x.username,
)


def google_login(request):
    redirect_uri = "%s://%s%s" % (
        request.scheme, request.get_host(), reverse('google-login')
    )
    if 'code' in request.GET:
        params = {
            'grant_type': 'authorization_code',
            'code': request.GET.get('code'),
            'redirect_uri': redirect_uri,
            'client_id': settings.GP_CLIENT_ID,
            'client_secret': settings.GP_CLIENT_SECRET
        }
        url = 'https://accounts.google.com/o/oauth2/token'
        response = requests.post(url, data=params)
        url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        access_token = response.json().get('access_token')
        response = requests.get(url, params={'access_token': access_token})
        user_data = response.json()
        email = user_data.get('email')
        if email:
            user, created = User.objects.get_or_create(username=email, email=email)
            if created:
                data = {
                    'first_name': user_data.get('given_name'),
                    'last_name': user_data.get('family_name'),
                    'is_active': True
                }
                user.__dict__.update(data)
                user.save()
            login(request, user)
            # messages.info(request, "Single sign-on session started for %s" % user)

            service = base64.b64decode(request.GET.get('state')).decode()
            if service:
                st = ServiceTicket.objects.create_ticket(service=service, user=user, primary=True)
                return cas_redirect(service, params={'ticket': st.ticket})
            return redirect('cas_login')
        else:
            messages.error(
                request,
                'Unable to login with Gmail Please try again'
            )
        return redirect(urllib.parse.urljoin(f'{request.scheme}://{request.get_host()}', 'login'))
    else:
        service = request.GET.get('service')
        if service:
            state = base64.b64encode(service.encode()).decode()
        else:
            state = 'google'
        url = "https://accounts.google.com/o/oauth2/auth" \
              "?client_id={client_id}" \
              "&response_type=code" \
              "&scope={scope}" \
              "&redirect_uri={redirect_uri}" \
              "&state={state}" \
              "&prompt=select_account"
        scope = [
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
        scope = " ".join(scope)
        url = url.format(client_id=settings.GP_CLIENT_ID, scope=scope, redirect_uri=redirect_uri, state=state)
        return redirect(url)
