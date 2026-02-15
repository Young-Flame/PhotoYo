# 📸 PhotoYo - Goth Punk Photography Portfolio

![License](https://img.shields.io/badge/license-MIT-ff00ff)
![Python](https://img.shields.io/badge/python-3.8+-00ffff)
![Flask](https://img.shields.io/badge/flask-3.0+-ff00ff)
![Status](https://img.shields.io/badge/status-active-00ffff)

> Rebel photography for the bold. No corporate BS, just raw moments captured through our lens.

A dark, edgy photography portfolio web application built with Flask. Features a cyberpunk-inspired goth punk aesthetic with magenta and cyan neon accents, edge-to-edge galleries, and an unapologetically bold design.


##Link For Live Demo which is running through pythoneverywhere
https://bibekthatall.pythonanywhere.com
## 🔥 Features

### Core Functionality
- **Full-Screen Gallery** - Zero-gap, edge-to-edge image grid with lightbox viewer
- **User Authentication** - Secure login/registration with role-based access (Admin/User)
- **Photo Management** - Upload, edit, delete photos with categories and metadata
- **Booking System** - Service booking requests with status tracking
- **Contact Forms** - Client inquiry submission and management
- **Dashboard** - User/Admin dashboards with statistics and recent activity
- **Comments & Likes** - Social engagement on photos
- **Responsive Design** - Mobile-first, works on all devices

### Design Features
- 🖤 **Goth Punk Aesthetic** - Dark backgrounds with neon magenta/cyan accents
- ⚡ **Edge-to-Edge Layouts** - No wasted space, full-bleed imagery
- 💀 **Bold Typography** - Heavy weights, uppercase styling, aggressive hierarchy
- 🎯 **Hover Effects** - Glows, transforms, and color inversions
- 📱 **Mobile Optimized** - Hamburger menus, touch-friendly interfaces
- 🌈 **Alternating Colors** - Magenta/cyan border patterns throughout

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
Flask 3.0+
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/photoyo.git
cd photoyo
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install flask flask-session werkzeug
```

4. **Create required directories**
```bash
mkdir -p static/uploads static/css static/js templates
```

5. **Run the application**
```bash
python app.py
```

6. **Access the app**
```
http://localhost:5000
```

### Default Admin Login
```
Email: admin@photo.com
Password: admin123
```

## 🎨 Design System

### Color Palette
```css
--primary-color: #ff00ff;    /* Magenta - Primary accent */
--secondary-color: #00ffff;  /* Cyan - Secondary accent */
--dark-color: #0a0a0a;       /* Pure black background */
--dark-purple: #1a0a1a;      /* Dark purple for gradients */
--light-color: #e0e0e0;      /* Light gray text */
--text-color: #b0b0b0;       /* Medium gray text */
--bg-dark: #1a1a1a;          /* Dark card backgrounds */
```

### Typography
- **Font Stack**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Headings**: 700-900 weight, uppercase, 1-3px letter-spacing
- **Body**: 1rem (16px), 400-600 weight
- **Accents**: Gradient text effects (magenta → cyan)

### Components
- **Bordered Cards**: 2-3px solid borders, alternating magenta/cyan
- **Buttons**: Transparent with border, fill on hover
- **Grid Layouts**: Zero-gap galleries, auto-fill responsive grids
- **Navigation**: Sticky header, magenta bottom border, hamburger mobile menu

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **Flask-Session** - Server-side session management
- **Werkzeug** - Password hashing and file handling

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom styling (no frameworks)
- **Vanilla JavaScript** - Interactive features
- **Font Awesome 6.4.0** - Icons

### Storage
- **In-Memory** - Users, photos, bookings, contacts (resets on restart)
- **File System** - Photo uploads stored in `/static/uploads`

## 📸 Usage

### For Users
1. **Browse Gallery** - View photos in edge-to-edge grid
2. **Register Account** - Create user profile
3. **Upload Photos** - Share your work (requires login)
4. **Book Services** - Request photography sessions
5. **Contact** - Send inquiries via contact form

### For Admins
1. **Manage Users** - View, delete, toggle admin roles
2. **Manage Photos** - Upload, edit, delete any photo
3. **Manage Bookings** - Review and update booking status
4. **View Contacts** - Access all contact form submissions
5. **Dashboard Stats** - Monitor users, photos, bookings

## 🎯 Key Routes

```python
/                      # Home page with featured photos
/gallery               # Full-screen photo gallery
/about                 # About page
/services              # Services and pricing
/contact               # Contact form
/login                 # User/Admin login
/register              # New user registration
/dashboard             # User/Admin dashboard
/photo/upload          # Upload new photo
/photo/<id>            # Photo detail view
/booking/create        # Create booking request
/admin                 # Admin panel (admin only)
/admin/users           # User management (admin only)
```

## 🔐 Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control (Admin/User)
- Secure file upload with extension validation
- CSRF protection via Flask-Session

## 🎭 Customization

### Change Colors
Edit `static/css/goth_punk_style.css`:
```css
:root {
    --primary-color: #YOUR_COLOR;
    --secondary-color: #YOUR_COLOR;
}
```

### Change Logo
Edit `templates/base.html`:
```html
<a href="/" class="logo">
    <i class="fas fa-camera"></i>
    <span>YourName</span>
</a>
```

### Add More Services
Edit `templates/services.html` and add new service cards following the existing pattern.

## 📱 Responsive Breakpoints

```css
Mobile:        < 480px   (2 column gallery)
Tablet:        480-768px (3-4 column gallery)
Desktop:       768-1200px (4-5 column gallery)
Large Desktop: > 1200px  (5-6 column gallery)
```

## 🐛 Known Issues

- Data resets on server restart (in-memory storage)
- No database persistence
- No email notifications
- Basic image compression

## 🚧 Future Enhancements

- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Email notifications for bookings
- [ ] Payment integration
- [ ] Advanced photo editing
- [ ] Social media sharing
- [ ] Blog/News section
- [ ] Multi-language support
- [ ] Image optimization/compression
- [ ] Search functionality
- [ ] Export booking data

<div align="center">

Made with 🖤 and ☕ by rebels for rebels

[⬆ Back to Top](#-photoyo---goth-punk-photography-portfolio)

</div>
