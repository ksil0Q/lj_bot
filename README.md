# This is lj_bot version 1.0.0

The bot aims to support the used auto parts market by acting as a platform between sellers and buyers of auto parts. Uses aiogram3, aiohttp, peewee-async and PostgreSQL.
ngrok is used locally to run (with key pair generated via openssl).

If you intend to work locally using ngrok, you can:
1. manually start ngrok and move the issued address to .env
2. run setup.ps1 (on win), which will start ngrok and change the address automatically

the etc/scripts/sql directory contains sql files for initial database configuration and filling_in_auto_tables.py which will fill the database with popular brands and their car models

The parameters that the application expects to see in .env
1. API_TOKEN - your bot's token in the telegram
2. DATABASE_NAME
3. USER - username
4. PASSWORD - the password for accessing the database
5. DB_HOST - the address of the database
6. DB_PORT - database port
7. WEB_SERVER_HOST - the address where the http aio will wait for an update
8. WEB_SERVER_PORT is one of the following: 80, 88, 443, 8,443
9. WEBHOOK_SSL_PRIV - private key
10. WEBHOOK_SSL_CERT - certificate (can be self-signed)
11. MAX_BRANDS_IN_ROW - optimally 3
12. MAX_MODELS_IN_ROW - optimally 3
13. MAX_DETAIL_MENU_SECTIONS_IN_ROW - optimal 2
14. MAX_TARIFFS_IN_ROW - optimal 2
15. MAX_INLINE_BUTTONS - number of buttons in the menu, optimal 5
16. MAX_CODE_LEN - the length of the codec to identify the payment, at your discretion


briefly about the work of the bot
At the start, the user chooses a role (buyer or seller). Agrees to the terms of use (I did not invent them).

When choosing the role of the buyer, the user can choose his car - /change_my_car. After that, he can go to the menu - /menu and select the categories of parts, the bot will offer all ads for parts with the same category for the selected car. The ad will include the price, description, link to the seller and a photo of the part. Any buyer can become a seller - /become_a_seller or /choose_a_tariff.
The buyer also has access to a personal account - /my_office or /help (it lists all available commands)

Any seller has all the functionality of a buyer, that is, his role is to expand the role of the buyer. In order to become a seller, you need to choose one of the proposed tariffs and attach the code received from the bot to the payment message. Wait for confirmation from the administration. The seller can post ads - /create_advertisement and close them - /close_advertisement.

Any admin has all the functionality of a seller and a buyer. Can confirm payment - /confirm_payment, ban users - /block_a_user and /unblock_a_user