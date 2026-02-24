"""Database initialization script."""
import os
from app import create_app
from app.models import db
from app.services.auth_service import AuthService
from app.services.service_manager import ServiceManager

def init_database():
    """Initialize the database with default data."""
    app = create_app('development')
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create default admin user
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        print(f"Creating admin user: {admin_username}")
        admin = AuthService.create_admin(admin_username, admin_password)
        
        if admin:
            print(f"✓ Admin user created successfully")
            print(f"  Username: {admin_username}")
            print(f"  Password: {admin_password}")
            print(f"  IMPORTANT: Change this password after first login!")
        else:
            print("✗ Admin user already exists or creation failed")
        
        # Create default services
        print("\nCreating default services...")
        
        services_data = [
            {
                'name': 'Получить путевку',
                'description': 'Получение путевки в лагерь',
                'documents': [
                    'Оригинал и копия свидетельства о рождении ребенка (даже если ребенок получил паспорт)',
                    'Распечатанная квитанция об оплате (полная, где видны все суммы и реквизиты)',
                    'Оригинал паспорта родителя для заполнения договора об оказании услуги летнего отдыха'
                ]
            },
            {
                'name': 'Возврат денежных средств',
                'description': 'Возврат денежных средств за путевку',
                'documents': [
                    'Оригинал путевки',
                    'Паспорт родителя',
                    'Реквизиты для возврата средств'
                ]
            },
            {
                'name': 'Возврат путевки',
                'description': 'Возврат неиспользованной путевки',
                'documents': [
                    'Оригинал путевки',
                    'Паспорт родителя'
                ]
            }
        ]
        
        for service_data in services_data:
            service = ServiceManager.create_service(
                name=service_data['name'],
                description=service_data['description'],
                required_documents=service_data['documents']
            )
            
            if service:
                print(f"✓ Created service: {service.name}")
            else:
                print(f"✗ Service already exists: {service_data['name']}")
        
        print("\n" + "="*50)
        print("Database initialization complete!")
        print("="*50)
        print("\nYou can now run the application with:")
        print("  python run.py")
        print("\nAdmin panel URL:")
        print("  http://localhost:5000/admin/login")
        print(f"\nLogin credentials:")
        print(f"  Username: {admin_username}")
        print(f"  Password: {admin_password}")
        print("\n⚠️  IMPORTANT: Change the admin password after first login!")


if __name__ == '__main__':
    init_database()
