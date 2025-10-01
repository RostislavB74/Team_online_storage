# Users Auth flow

## Реєстрація користувача
1. реєстрація за email + password тільки.

2. usename = email автоматично після реєстрації.

3. Якщо сервер підтримує Пошту то процес реєстрації та авторизації та видалення користувача, проходить через підтвердження на пошту за допомогою одноразового паролю (OTP).

Register answer: 
```json
{
"status": "success",
"message": "Registration successful. ",
"user_id": 59,
"username": "test_01@example.com"
}
```
Де:
- status - "success"  - без OTP password
- status - "otp_sent"  - з OTP password

Відповідно і registration flow має бути різний - запитувати OTP з email чи ні.

## Request Auth
Request HEADER  -H 'Authorization: Token e1d0485c411f670a0f7f6e9570b0dd910111b540'
Token постійний поки користувач не зробить logout, тобто його оновлювати не потрібно, можна зберегти у local Storage.

## Logout 
Logout для авторизованого користувача:

## LOGIN
Login (/api/v1/auth/login/) відрізняться від get token (/api/v1/auth/token/)  тим що потребує перевірки через OTP для отримання токену.
Це тема для дискусій чи потрібно це робити. 
Ідея: (/api/v1/auth/token/) видає токен поки користувач ще не зробив logout (/api/v1/auth/logout/). Зробив logout то тільки через login.

## LOGIN FLOW:
* Check if the token is present in local storage. If it is, use it for Authorization. 

* If the token is not present in local storage, prompt the user for their email and password, then send an API request to {{URL}}/auth/token/. If the response is OK, save the token to local storage and use it for Authorization in headers.

* If {{URL}}/auth/token/ responds with a 403 code, it indicates that the token needs to be generated through the login process using OTP.

* To log in, use the user's email and password and send them to {{URL}}/auth/login/. If the response status is "otp_sent," open the page to enter the OTP code, prompt the user for their OTP, and send it to the API at {{URL}}/auth/register/verify/. Once verified, store the token in local storage for subsequent authorizations via the Header.