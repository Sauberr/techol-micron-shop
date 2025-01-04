### 🚀 Micron: Your One-Stop Shop for High-Performance Computer Hardware 🚀

Micron is a cutting-edge online store specializing in computer hardware, built with Django 4.2 and Python. It's designed to provide a seamless and efficient shopping experience for tech enthusiasts. This project leverages a powerful backend stack, including PostgreSQL, Celery, Redis, RabbitMQ, and Docker, to ensure optimal performance, scalability, and reliability.

With Micron, customers can explore a vast selection of computer hardware products and easily find what they need using user-friendly filtering options and a robust search functionality. The store also offers intelligent product recommendations, ensuring customers discover items perfectly tailored to their interests. Enjoy a smooth and enjoyable shopping journey with features like convenient shopping cart management, coupon utilization for discounts, and secure order tracking.

Micron is not just about the frontend experience; it also boasts a powerful admin panel that allows for efficient management of products through CRUD operations. Furthermore, a comprehensive API built with Django REST Framework (DRF) provides seamless integration with other services, featuring search and pagination for enhanced flexibility.

This project exemplifies modern e-commerce development practices, offering a dynamic and feature-rich online store for buying and selling computer hardware. Micron supports both English and Ukrainian languages, catering to a wider audience and providing a personalized experience. By combining a robust backend with a user-friendly interface, Micron delivers a truly exceptional online shopping experience for all your computer hardware needs.

## Stack:

- [Python](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [Celery](https://docs.celeryq.dev/en/stable/)
- [Docker](https://www.docker.com/)
- [DRF](https://www.django-rest-framework.org/)
- [RabbitMQ](https://www.rabbitmq.com/)

## Local Developing

All actions should be executed from the source directory of the project and only after installing all requirements.

1. Firstly, create and activate a new virtual environment:
   ```bash
   python3.11 -m venv ../venv
   source ../venv/bin/activate
   ```
   
2. Install packages:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   
3. Run project dependencies, migrations, fill the database with the fixture data etc.:
   ```bash
   ./manage.py migrate
   ./manage.py loaddata <path_to_fixture_files> 
   ```

4. Install redis:
   ```bash
   redis-server
   ```

5. Install celery:
   ```bash
   celery -A app name worker -l INFO --pool=solo
   ```
   
6. Docker :
   ```bash
   docker run -it --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
   
   docker run -it --rm --name redis -p 6379:6379 redis
   ```

7. Stripe :
   ```bash
   stripe listen --forward-to localhost:8000/payment/webhook/
   ```

## License

This project uses the [MIT] license(https://github.com/Sauberr/techol-micron-shop/blob/master/LICENSE)

## Contact 

sauberr10@gmail.com
