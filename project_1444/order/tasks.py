# from celery import shared_task
# from django.core.mail import send_mail
# from liqpay import LiqPay

# @shared_task
# def send_order_confirmation_email(order_id, user_email):
#     """
#     Асинхронна задача для відправки email після створення замовлення.
#     """
#     try:
#         send_mail(
#             subject='Замовлення підтверджено',
#             message=f'Ваше замовлення #{order_id} оформлено!',
#             from_email='from@example.com',
#             recipient_list=[user_email],
#             fail_silently=True,
#         )
#     except Exception as e:
#         # Логування помилок
#         from logging import getLogger
#         logger = getLogger(__name__)
#         logger.error(f"Помилка відправки email для замовлення #{order_id}: {e}")



# @shared_task
# def create_liqpay_payment(order_id, amount):
#     liqpay = LiqPay('public_key', 'private_key')
#     params = {
#         'action': 'pay',
#         'amount': str(amount),
#         'currency': 'UAH',
#         'description': f'Замовлення #{order_id}',
#         'order_id': str(order_id),
#         'version': '3',
#         'result_url': 'https://your-site.com/order/confirmation/',
#         'server_url': 'https://your-site.com/api/liqpay/callback/'
#     }
#     return liqpay.cnb_form(params)