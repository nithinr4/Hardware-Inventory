from app import app, db
from models import User, Hardware, Checkout
from werkzeug.security import generate_password_hash
import random
from datetime import datetime


def populate_db():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create sample users
        user1 = User(username='Adit', password_hash=generate_password_hash('123456'), privilege_level='user')
        user2 = User(username='Vikky', password_hash=generate_password_hash('123456'), privilege_level='admin')
        user3 = User(username='Goutham', password_hash=generate_password_hash('Modbus'), privilege_level='admin')
        user4 = User(username='Nithin', password_hash=generate_password_hash('123456'), privilege_level='admin')

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.add(user4)
        db.session.commit()

        # Create sample hardware items
        stm_boards = ['STM32 Nucleo-F429ZI', 'STM32 Nucleo-G431RB', 'STM32 F4-Discovery', 'STM32 Nucleo-H743ZI']
        tic2000_boards = ['TI C2000 F2838xD', 'TI C2000 F2834x', 'TI C2000 F28M35x', 'TI C2000 F28002x']
        ifx_boards = ['Aurix TC499A COM', 'Aurix TC499A STD', 'Aurix TC4D', 'Aurix TC3x']
        for i in range(len(stm_boards)):
            hardwareBoardSTM = Hardware(name=stm_boards[i], count=random.randint(1,5), owner_id=user4.id)
            hardwareBoardTI = Hardware(name=tic2000_boards[i], count=random.randint(1,5), owner_id=user3.id)
            hardwareBoardIfx = Hardware(name=ifx_boards[i], count=random.randint(1,5), owner_id=user2.id)

            db.session.add(hardwareBoardSTM)
            db.session.add(hardwareBoardTI)
            db.session.add(hardwareBoardIfx)

        # Add users and hardware to the session
        db.session.commit()

# # Create sample checkouts
# checkout1 = Checkout(user_id=user1.id, hardware_id=hardware1.id, checkout_date=datetime.now())
# checkout2 = Checkout(user_id=user2.id, hardware_id=hardware2.id, checkout_date=datetime.now())

# # Add checkouts to the session
# db.session.add(checkout1)
# db.session.add(checkout2)
# db.session.commit()

print("Database populated with sample data.")

if __name__ == '__main__':
    populate_db()
