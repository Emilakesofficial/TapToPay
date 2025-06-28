# TapToPay – Smart POS Backend System

TapToPay is a modular, scalable backend POS system built with Django & DRF.Designed for merchant flexibility and robust financial tracking. It supports customizable merchant charges, cart checkout, real-time stock tracking, payment verification, and detailed reporting. Built for modern fintech environments, ideal for merchants and retail environments.

# Features

- JWT Authentication with OTP and Password Reset

- Cart & Checkout System

- Paystack Integration for Secure Payments.

- Merchant Customization (Tax, Service Fee, Tip)

- Daily and Per-Transaction Reporting

- Stock Management & Low Stock Alerts

- Modular Architecture (Each service in its own app)

Dockerized & Ready for Cloud Deployment

🔹 Modular Apps

App description

user ------- Authentication, profiles, OTP

product ------- Product data, stock tracking

checkout ------- Cart logic, add/remove/clear items

payment ------- Handles Paystack init & verify

merchant ------- Custom tax, tips, and service fees

report ------- Tracks daily and individual transactions

# Daily Reporting
Auto-generated on successful/failed payments
Tracks:
Total sales amount
Total number of transactions
Successful and failed counts

# Per-Transaction Reporting
Tracks each transaction including:
User (Full Name)
Payment Reference
Status (Success/Failed)
Amount paid
Associated Merchant
Timestamp

##  Tech Stack

- **Backend**: Django + Django REST Framework
- **Auth**: JWT (Simple JWT)
- **Payments**: Paystack API
- **Docs**: Swagger (drf-yasg)
- **DB**: SQLite (easily swappable to Postgres/MySQL)

# API Endpoint Screenshots
 ## users app
- **Register**  
  ![alt text](screenshots/register.png)

- **Verify Email**  
  ![alt text](screenshots/verify_email.png)


- **Resend Email**  
![alt text](screenshots/resend_email.png)

- **Login / Token**  
![alt text](screenshots/login.png)
![alt text](get_login_token.png)

- **Get Profile**  
![alt text](screenshots/get_profile.png)

- **Update Profile** 
![alt text](screenshots/update_profile.png) 

- **Change Password Flow**  
![alt text](screenshots/verify_old_password.png)
![alt text](screenshots/verify_old_password_otp.png)
![alt text](screenshots/change_password.png)

- **Forgot Password Flow**
![alt text](screenshots/forgot_password.png)
![alt text](screenshots/verify_forget_password_otp.png)
![alt text](screenshots/reset_password.png)

- **logout**
![alt text](screenshots/logout.png)

**country flow**
![alt text](screenshots/add_country.png)
![alt text](screenshots/get_countries.png)
![alt text](screenshots/update_country.png)
![alt text](screenshots/delete_country.png)


## product
**custom unit flow**
![alt text](screenshots/add_custom_unit.png)
![alt text](screenshots/get_custom_unit.png)
![alt text](screenshots/update_custom_unit.png)
![alt text](screenshots/delete_custom_unit.png)

**Product Flow**
![alt text](screenshots/add_product.png)
![alt text](screenshots/get_single_product.png)
![alt text](screenshots/get_products.png)
![alt text](screenshots/update_product.png)
![alt text](screenshots/delete_product.png)

- **Merchant settings Endpoints**
![alt text](screenshots/get_merchant_settings.png)
![alt text](screenshots/update_merchant_settings.png)

## Checkout app
![alt text](screenshots/add_to_cart.png)
![alt text](screenshots/remove_from_cart.png)
![alt text](screenshots/get_cart.png)
![alt text](screenshots/checkout_summary.png)

## Payment app
![alt text](screenshots/initialize_payment.png)
![alt text](screenshots/verify_payment.png)

## report app
![alt text](screenshots/daily_sales_report.png)
![alt text](screenshots/transaction_report.png)

**Contact**
For inquiries or collaboration:
📧 adegbemiadekunle56@gmail.com
🔗 LinkedIn : https://www.linkedin.com/in/adekunle-adegbemi-4b590a346?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app