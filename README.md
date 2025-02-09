# TeamChallenge.io_1345_edu
Team Challenge project #1345. Test and education with git. Any action from co-owners.

## Swager docs ...
URL: / or /docs/swagger/

![Screenshot 2025-01-24 at 00-45-26 PROJECT 1345 - API](https://github.com/user-attachments/assets/8bbbfff7-58b0-4429-a499-e47a7606111d)


## ReDoc
### Product List 
URL: /docs/redoc/

![Знімок екрана 2025-01-22 о 22 03 41](https://github.com/user-attachments/assets/27327cec-d9aa-4506-8fab-c101ea03fadf)


## Django REST framework GUI for API
### Product List/Create 
URL: /api/v1/products/

![Screenshot 2025-01-22 at 21-57-19 Product List – Django REST framework](https://github.com/user-attachments/assets/1dd5d371-db28-4e9a-a885-c7cf4299847a)

## Django Admin
Uploaded image:
![Знімок екрана 2025-01-23 о 05 10 44](https://github.com/user-attachments/assets/57e0b75e-e87b-4405-a008-384f33f78ec9)


## Demo Users:
Retrieve a list of demo users. It temporarily stores them in the cache. Build on start up.

URL: /api/v1/users/demo/

![Знімок екрана 2025-01-24 о 00 34 42](https://github.com/user-attachments/assets/a435d4ed-95ff-4636-8747-9ac92c2c003e)

## API

### Cart 
/api/v1/cart
#### GET
```json
[
    {
        "product_id": 1,
        "product_name": "item1",
        "quantity": 4,
        "price": "100.00",
        "total_price": "400.00"
    },
    {
        "product_id": 2,
        "product_name": "item2",
        "quantity": 1,
        "price": "200.00",
        "total_price": "200.00"
    }
]
```
#### POST
```json
{
 "product_id": 1,
 "quantity": 1,
 "price": 100.00
}
```
#### DELETE
Can delete one product:
```json
{"product_id": 1}
```
Or without any data can delete all item's cart


### Deployed education version

https://teamchallenge-io-1345-edu.onrender.com

