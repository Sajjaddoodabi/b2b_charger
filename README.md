# B2B Charger

A **Django-based B2B recharge credit system** that enables vendors to request top-ups, admins to approve them, and vendors to sell credit through phone number–based transactions.  
The system ensures **atomic operations**, **balance integrity**, and **secure transaction logging**, even under heavy concurrency.

---

## 🚀 Features

- **Vendor Credit Management**
  - Vendors request credit top-ups.
  - Admin approval workflow for requests.
  - Real-time balance tracking.

- **Phone Number–Based Transactions**
  - Vendors sell credit using customer mobile numbers.
  - Prevents invalid or duplicate transactions automatically.

- **Atomic & Concurrency-Safe**
  - Race-condition–free balance updates.
  - Prevents negative balances in all flows.
  - Stress-tested with parallel requests.

- **Transaction Logging**
  - Complete audit trail for top-ups and sales.
  - Vendor balance history and reporting.

- **Admin Dashboard**
  - Approve recharge requests.
  - Monitor system activity and export reports.

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework  
- **Database:** MySQL (transaction-safe with strict integrity checks)  
- **Task Queue:** Celery + Redis (async jobs & concurrency)  
- **Authentication:** JWT with role-based permissions  
- **Deployment:** Docker-ready  
- **Testing:** Pytest for unit + concurrency stress tests  

---

## 📂 Project Structure
b2b_charger
- core # Core settings & utilities
- phone_number # Recharge logic based on phone numbers
- transaction # Payment & transaction workflows
- user # User and role management
- vendor # Vendor credit and approval handling
- utils # Shared helpers
- requirements.txt

---

## ⚡ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Sajjaddoodabi/b2b_charger.git
cd b2b_charger
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run database migrations
```bash
python manage.py migrate
```

### 4. Start the development server
```bash
python manage.py runserver
```


## 🧪Running Tests
```bash
pytest
```

**Covers**:
- Unit tests for models, views, and serializers
- Concurrency stress tests for financial transactions



