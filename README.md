# Santamore Feeds - Digital Cooperative Platform

A web-based platform enabling Central Kenya smallholder farmers to access wholesale feed prices through group buying.

## Features

- **Zone-based Group Buying**: Farmers in the same zone pool orders to unlock bulk discounts
- **Automated Discount System**: 15% discount automatically applied when zone reaches 300kg target
- **M-Pesa Integration**: Secure STK Push payments via Safaricom Daraja API
- **User Authentication**: Registration with phone number and zone selection
- **Product Catalog**: Dairy, poultry, and pig feed management
- **Order Tracking**: Real-time order status and payment confirmation

## Tech Stack

- **Backend**: Django 6.0, Python 3.12
- **Frontend**: Bootstrap 5, Font Awesome icons
- **Database**: SQLite (development), PostgreSQL-ready
- **Payment**: M-Pesa Daraja API
- **Authentication**: Django built-in auth system

## Database Schema

- **Zone**: Location-based groups with discount thresholds
- **UserProfile**: Links users to zones and phone numbers
- **Product**: Feed inventory with pricing and stock
- **Order**: Purchase records with status tracking
- **Payment**: M-Pesa transaction records

## How Group Buying Works

1. Farmers register with their zone (e.g., Nyeri Town)
2. System tracks total weight of pending orders per zone
3. When zone reaches 300kg target, 15% discount activates
4. All farmers in that zone get discounted prices
5. Orders are processed and dispatched together

## Future Enhancements

- SMS notifications for order updates
- Advanced analytics dashboard
- Multiple discount tiers
- Delivery tracking system
- Mobile app (React Native)

## Author

Tabitha Gichuki - eMobilis Project 2025


