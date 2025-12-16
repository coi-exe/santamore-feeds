from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from feeds.models import Order
from .models import Payment
import json
import requests
from decouple import config
import base64
from datetime import datetime

def get_mpesa_token():
    """Get OAuth access token from M-Pesa"""
    consumer_key = config('MPESA_CONSUMER_KEY')
    consumer_secret = config('MPESA_CONSUMER_SECRET')
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    return response.json().get('access_token')

@login_required
def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    phone = request.user.userprofile.phone_number
    
    # Create payment record
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'phone_number': phone,
            'amount': order.total_amount,
            'status': 'PENDING'
        }
    )
    
    context = {
        'order': order,
        'payment': payment,
    }
    return render(request, 'checkout.html', context)

@login_required
def trigger_stk_push(request, payment_id):
    """Trigger M-Pesa STK Push"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    try:
        # Get access token
        access_token = get_mpesa_token()
        
        # Format phone number
        phone = payment.phone_number
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif not phone.startswith('254'):
            phone = '254' + phone
        
        # STK Push parameters
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        shortcode = config('MPESA_SHORTCODE')
        passkey = config('MPESA_PASSKEY')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode('utf-8')
        
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(payment.amount),
            "PartyA": phone,
            "PartyB": shortcode,
            "PhoneNumber": phone,
            "CallBackURL": "https://yourdomain.com/payments/callback/",
            "AccountReference": f"Order{payment.order.id}",
            "TransactionDesc": "Santamore Feeds Payment"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        response_data = response.json()
        
        if response_data.get('ResponseCode') == '0':
            messages.success(request, 'Payment prompt sent to your phone! Please enter your M-Pesa PIN.')
            return redirect('payment_status', payment_id=payment.id)
        else:
            messages.error(request, f'Payment failed: {response_data.get("errorMessage", "Unknown error")}')
            return redirect('initiate_payment', order_id=payment.order.id)
        
    except Exception as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('initiate_payment', order_id=payment.order.id)

@login_required
def payment_status(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payment_status.html', context)

@csrf_exempt
def mpesa_callback(request):
    """M-Pesa callback endpoint - receives payment confirmation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Log the callback for debugging
            print("M-Pesa Callback received:", data)
            
            result_code = data['Body']['stkCallback']['ResultCode']
            
            if result_code == 0:  # Success
                # Extract transaction details
                callback_metadata = data['Body']['stkCallback']['CallbackMetadata']['Item']
                
                # Find the receipt number
                mpesa_receipt = None
                for item in callback_metadata:
                    if item['Name'] == 'MpesaReceiptNumber':
                        mpesa_receipt = item['Value']
                        break
                
                # Update payment status
                payment = Payment.objects.filter(status='PENDING').order_by('-created_at').first()
                
                if payment:
                    payment.status = 'COMPLETED'
                    payment.mpesa_receipt = mpesa_receipt
                    payment.transaction_date = datetime.now()
                    payment.save()
                    
                    # Update order status
                    payment.order.status = 'PAID'
                    payment.order.save()
            
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
            
        except Exception as e:
            print(f"Callback error: {str(e)}")
            return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})
    
    return HttpResponse("Callback endpoint")

@login_required
def manual_confirm_payment(request, payment_id):
    """Manual payment confirmation (for testing/demo purposes)"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment.status = 'COMPLETED'
        payment.mpesa_receipt = 'DEMO' + str(payment.id).zfill(10)
        payment.transaction_date = datetime.now()
        payment.save()
        
        payment.order.status = 'PAID'
        payment.order.save()
        
        messages.success(request, 'Payment confirmed! (Demo Mode)')
        return redirect('payment_status', payment_id=payment.id)
    
    return redirect('payment_status', payment_id=payment.id)