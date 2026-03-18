El Edificio Conectado 🏢 - Django Multi-Tenant SaaS

El Edificio Conectado es una plataforma profesional de gestión inmobiliaria diseñada bajo el modelo SaaS (Software as a Service). Permite a administradores y dueños de edificios gestionar múltiples propiedades, inquilinos y contratos de forma aislada y segura mediante una arquitectura de base de datos multi-esquema.
🌟 Características Principales

    🚀 Arquitectura Multi-tenant: Aislamiento total de datos por cliente mediante esquemas de PostgreSQL (django-tenants).

    📄 Gestión Documental: Carga y visualización de contratos notarizados en PDF con almacenamiento dinámico por unidad.

    🔍 Búsqueda Avanzada: Integración de Select2 para búsqueda inteligente de inquilinos y DataTables para listados masivos.

    💳 Control Financiero: Seguimiento de rentas mensuales, depósitos de garantía y estados de cuenta (Pagado, Pendiente, Atrasado).

    🏠 Gestión de Inventario: Control de disponibilidad de unidades (departamentos/locales) en tiempo real.

    🛠️ Dockerizado: Entorno de desarrollo y producción listo para desplegar con Docker y Docker Compose.

    🎨 UI Profesional: Basado en AdminLTE 3 para una experiencia de usuario administrativa fluida y responsiva.

🛠️ Stack Tecnológico

    Backend: Django 5.0.8 / Python 3.12

    Base de Datos: PostgreSQL (con soporte de esquemas para Multi-tenancy)

    Frontend: Bootstrap 4, AdminLTE 3, jQuery, Select2, DataTables

    Infraestructura: Docker & Docker Compose, Nginx

    Lógica de Negocio: Django Tenants, Reportes financieros personalizados

📁 Estructura del Proyecto
Plaintext

├── apps/
│   ├── core/           # Lógica central del sistema (Public schema)
│   ├── lease/          # Gestión de inquilinos y contratos (Tenant schema)
│   ├── billing/        # Facturación y cobros (Tenant schema)
│   └── users/          # Autenticación y perfiles
├── media/              # Archivos subidos (Contratos PDF)
├── static/             # Archivos estáticos (CSS, JS, AdminLTE)
├── docker-compose.yml  # Configuración de contenedores
└── .env.example        # Plantilla de variables de entorno

🚀 Inicio Rápido (Quick Start)

Sigue estos pasos para levantar el proyecto en tu entorno local:
1. Clonar y Configurar
Bash

git clone https://github.com/tu-usuario/el-edificio-conectado.git
cd el-edificio-conectado
cp .env.example .env

    Nota: Edita el archivo .env y coloca tu SECRET_KEY y credenciales de base de datos.

2. Levantar con Docker
Bash

docker compose up -d --build

3. Configuración Inicial (Shell)

Al ser un sistema Multi-tenant, debemos crear primero el esquema público y luego nuestro primer cliente (Tenant).

Entra al contenedor de Django:
Bash

docker compose exec web python manage.py shell

Dentro del shell, ejecuta lo siguiente para crear el dominio público y el primer cliente:
Python

from apps.core.models import Client, Domain

# 1. Crear el esquema público (necesario para el login principal)
tenant = Client(schema_name='public', name='PublicSchema')
tenant.save()
Domain.objects.create(domain='localhost', tenant=tenant, is_primary=True)

# 2. Crear tu primer cliente (SaaS Tenant)
tenant2 = Client(schema_name='edificio_centro', name='Edificio Centro Histórico')
tenant2.save()
Domain.objects.create(domain='tenant2.localhost', tenant=tenant2, is_primary=True)

4. Crear Superusuario
Bash

docker compose exec web python manage.py createsuperuser

5. Acceder

    Página Principal: http://localhost:8000

    Panel del Cliente: http://tenant2.localhost:8000

🔒 Seguridad y Variables de Entorno

Este proyecto utiliza variables de entorno para proteger datos sensibles. Nunca subas el archivo .env al repositorio. Asegúrate de configurar:

    SECRET_KEY: Clave única para firmas criptográficas.

    DATABASE_URL: Conexión a PostgreSQL.

    DEBUG: Mantener en False en producción.

👨‍💻 Autor

Franklin Barreiro

Licencia - MIT
