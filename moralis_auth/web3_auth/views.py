"""Define API Views"""

import json
import requests

from moralis import auth

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


API_KEY = ""

# this is a check to make sure the the API key was set
# you have to set the API key only in line 9 above
# you don't have to change the next line
if API_KEY == 'WEB3_API_KEY_HERE':
    print("API key is not set")
    raise SystemExit


def moralis_auth(request):
    """
    Render the login form
    :param request:
    :return:
    """
    return render(request, 'login.html', {})


def my_profile(request):
    """
    Display profile information
    :param request:
    :return:
    """
    return render(request, 'profile.html', {})


def request_message(request):
    """
    Request a message
    :param request:
    :return:
    """
    data = json.loads(request.body)
    print(data)

    request_url = 'https://authapi.moralis.io/challenge/request/evm'
    request_object = {
        "domain": "defi.finance",
        "chainId": 1,
        "address": data['address'],
        "statement": "Please confirm",
        "uri": "https://defi.finance/",
        "expirationTime": "2023-01-01T00:00:00.000Z",
        "notBefore": "2020-01-01T00:00:00.000Z",
        "timeout": 15,
        # "resources": ['https://docs.moralis.io/'],
    }
    # x = requests.post(
    #     request_url,
    #     json=request_object,
    #     headers={'X-API-KEY': API_KEY}
    #     )

    body = {
        "domain": "defi.finance",
        "chainId": "1",
        "address": data['address'],
        "statement": "Please confirm",
        "uri": "https://defi.finance/",
        "expirationTime": "2023-01-01T00:00:00.000Z",
        "notBefore": "2020-01-01T00:00:00.000Z",
        "resources": ['https://docs.moralis.io/'],
        "timeout": 15,
    }

    result = auth.challenge.request_challenge_evm(
        api_key=API_KEY,
        body=body
    )

    print(f"result {result}")
    print(type(result))

    return JsonResponse(result)


def verify_message(request):
    """
    Verify message
    :param request:
    :return:
    """
    data = json.loads(request.body)
    print(data)

    # request_url = 'https://authapi.moralis.io/challenge/verify/evm'
    # x = requests.post(
    #     request_url,
    #     json=data,
    #     headers={'X-API-KEY': API_KEY})

    result = auth.challenge.verify_challenge_evm(
        api_key=API_KEY,
        body=data
    )
    print(f"result {result}")

    if result:
        eth_address =  result["address"]
        print(f"eth address {eth_address}")

        try:
            user = User.objects.get(username=eth_address)
        except User.DoesNotExist:
            user = User(username=eth_address)
            user.is_staff = False
            user.is_superuser = False
            user.save()
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['auth_info'] = data
                request.session['verified_data'] = result
                return JsonResponse({'user': user.username})
            else:
                return JsonResponse({'error': 'account disabled'})

    # print(json.loads(x.text))
    # print(x.status_code)
    #
    # if x.status_code == 201:
    #     # user can authenticate
    #     eth_address=json.loads(x.text).get('address')
    #     print("eth address", eth_address)
    #
    #     try:
    #         user = User.objects.get(username=eth_address)
    #     except User.DoesNotExist:
    #         user = User(username=eth_address)
    #         user.is_staff = False
    #         user.is_superuser = False
    #         user.save()
    #     if user is not None:
    #         if user.is_active:
    #             login(request, user)
    #             request.session['auth_info'] = data
    #             request.session['verified_data'] = json.loads(x.text)
    #             return JsonResponse({'user': user.username})
    #         else:
    #             return JsonResponse({'error': 'account disabled'})
    # else:
    return JsonResponse(result)
