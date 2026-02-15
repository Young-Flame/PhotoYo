"""
Photography Portfolio Web Application
Combines contact management, photo gallery, and booking system
Uses in-memory storage for simplicity (no database required)
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_session import Session # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
import os
import glob

# ==================== APP CONFIGURATION ====================
app = Flask(__name__)
app.config.update(
    SECRET_KEY='your-secret-key-change-in-production',
    SESSION_PERMANENT=False,
    SESSION_TYPE='filesystem',
    UPLOAD_FOLDER='static/uploads',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
)
Session(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ==================== DATA STORAGE ====================
# In-memory data structures (resets on app restart)
users = []      # User accounts with auth info
photos = []     # Photo gallery items
contacts = []   # Contact form submissions
bookings = []   # Service booking requests
comments = []   # Photo comments

# Auto-increment ID counters
next_id = {'user': 1, 'photo': 1, 'contact': 1, 'booking': 1, 'comment': 1}

# ==================== INITIALIZE ADMIN USER ====================
# Create admin user immediately on startup
users.append({
    'id': next_id['user'],
    'name': 'Admin User',
    'email': 'admin@photo.com',
    'phone': '+1234567890',
    'password_hash': generate_password_hash('admin123'),
    'role': 'admin',
    'created_at': datetime.utcnow()
})
next_id['user'] += 1
print('✓ Admin created: admin@photo.com / admin123')

# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator: Require user login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator: Require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = next((u for u in users if u['id'] == session['user_id']), None)
        if not user or user['role'] != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Home page with featured photos"""
    featured = sorted(photos, key=lambda x: x.get('views', 0), reverse=True)[:6]
    return render_template('index.html', photos=featured)

@app.route('/gallery')
def gallery():
    """Photo gallery with all uploaded images"""
    # Get images from upload folder
    images = []
    for ext in ALLOWED_EXTENSIONS:
        images.extend([os.path.basename(f) for f in glob.glob(f"{app.config['UPLOAD_FOLDER']}/*.{ext}")])
    return render_template('gallery.html', images=images, photos=photos)

@app.route('/about')
def about():
    """About page with statistics"""
    stats = {
        'total_photos': len(photos),
        'total_clients': len([u for u in users if u['role'] == 'user']),
        'total_bookings': len(bookings)
    }
    return render_template('pages/about.html', stats=stats)


@app.route('/services')
def services():
    """Services offered page"""
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form for inquiries"""
    if request.method == 'POST':
        # Save contact message
        contacts.append({
            'id': next_id['contact'],
            'name': request.form.get('name'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'message': request.form.get('message'),
            'created_at': datetime.utcnow()
        })
        next_id['contact'] += 1
        flash('Thank you! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('pages/contact.html')


@app.route('/photo/<int:photo_id>')
def photo_detail(photo_id):
    """Individual photo detail page"""
    photo = next((p for p in photos if p['id'] == photo_id), None)
    if not photo:
        flash('Photo not found.', 'danger')
        return redirect(url_for('gallery'))
    
    photo['views'] = photo.get('views', 0) + 1  # Increment view count
    photo_comments = [c for c in comments if c['photo_id'] == photo_id]
    return render_template('photos/photo_detail.html', photo=photo, comments=photo_comments)


# ==================== AUTH ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validation
        if not all([name, email, password]):
            flash('All fields required.', 'danger')
            return redirect(url_for('register'))
        
        if request.form.get('password') != request.form.get('confirm_password'):
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        if any(u['email'] == email for u in users):
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        users.append({
            'id': next_id['user'],
            'name': name,
            'email': email,
            'phone': request.form.get('phone', ''),
            'password_hash': generate_password_hash(password),
            'role': 'user',
            'created_at': datetime.utcnow()
        })
        next_id['user'] += 1
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User/Admin login"""
    session.clear()
    
    if request.method == 'POST':
        email = request.form.get('email') or request.form.get('username')
        password = request.form.get('password')
        
        user = next((u for u in users if u['email'] == email), None)
        
        if user and check_password_hash(user['password_hash'], password):
            # Set session variables
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    
    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    """Logout current user"""
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# ==================== USER DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User/Admin dashboard with stats"""
    user = next((u for u in users if u['id'] == session['user_id']), None)
    
    if user['role'] == 'admin':
        # Admin dashboard stats
        stats = {
            'total_users': len(users),
            'total_photos': len(photos),
            'pending_bookings': len([b for b in bookings if b.get('status') == 'pending']),
            'total_contacts': len(contacts)
        }
        recent_photos = sorted(photos, key=lambda x: x['created_at'], reverse=True)[:5]
        recent_bookings = sorted(bookings, key=lambda x: x['created_at'], reverse=True)[:5]
    else:
        # Regular user stats
        user_photos = [p for p in photos if p['user_id'] == user['id']]
        stats = {
            'my_photos': len(user_photos),
            'my_bookings': len([b for b in bookings if b.get('user_id') == user['id']]),
            'total_views': sum(p.get('views', 0) for p in user_photos)
        }
        recent_photos = sorted(user_photos, key=lambda x: x['created_at'], reverse=True)[:5]
        recent_bookings = sorted([b for b in bookings if b.get('user_id') == user['id']], 
                                key=lambda x: x['created_at'], reverse=True)[:5]
    
    return render_template('admin/dashboard.html', user=user, stats=stats, 
                          recent_photos=recent_photos, recent_bookings=recent_bookings)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    user = next((u for u in users if u['id'] == session['user_id']), None)
    
    if request.method == 'POST':
        user['name'] = request.form.get('name')
        user['phone'] = request.form.get('phone')
        if request.form.get('new_password'):
            user['password_hash'] = generate_password_hash(request.form.get('new_password'))
        session['user_name'] = user['name']
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('auth/profile.html', user=user)


# ==================== PHOTO MANAGEMENT ====================

@app.route('/photo/upload', methods=['GET', 'POST'])
@login_required
def upload_photo():
    """Upload new photo to gallery"""
    if request.method == 'POST':
        files = request.files.getlist('file') or [request.files.get('photo')]
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = datetime.now().strftime('%Y%m%d_%H%M%S_') + secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Add to photos database
                photos.append({
                    'id': next_id['photo'],
                    'title': request.form.get('title', 'Untitled'),
                    'description': request.form.get('description', ''),
                    'filename': filename,
                    'category': request.form.get('category', 'general'),
                    'views': 0,
                    'likes': 0,
                    'user_id': session['user_id'],
                    'created_at': datetime.utcnow()
                })
                next_id['photo'] += 1
        
        flash('Photo(s) uploaded successfully!', 'success')
        return redirect(url_for('gallery'))

    
    return render_template('photos/upload_photo.html')


@app.route('/photo/edit/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def edit_photo(photo_id):
    """Edit photo details"""
    photo = next((p for p in photos if p['id'] == photo_id), None)
    
    # Check permissions
    if not photo or (photo['user_id'] != session['user_id'] and session.get('user_role') != 'admin'):
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        photo['title'] = request.form.get('title')
        photo['description'] = request.form.get('description')
        photo['category'] = request.form.get('category')
        flash('Photo updated!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('admin/edit_photo.html', photo=photo)


@app.route('/photo/delete/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    """Delete photo from gallery"""
    global photos
    photo = next((p for p in photos if p['id'] == photo_id), None)
    
    if photo and (photo['user_id'] == session['user_id'] or session.get('user_role') == 'admin'):
        # Remove file from disk
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo['filename']))
        except:
            pass
        # Remove from database
        photos = [p for p in photos if p['id'] != photo_id]
        flash('Photo deleted!', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/photo/like/<int:photo_id>', methods=['POST'])
@login_required
def like_photo(photo_id):
    """Like a photo (AJAX)"""
    photo = next((p for p in photos if p['id'] == photo_id), None)
    if photo:
        photo['likes'] = photo.get('likes', 0) + 1
        return jsonify({'success': True, 'likes': photo['likes']})
    return jsonify({'success': False}), 404

@app.route('/photo/<int:photo_id>/comment', methods=['POST'])
@login_required
def add_comment(photo_id):
    """Add comment to photo"""
    content = request.form.get('content')
    if content:
        comments.append({
            'id': next_id['comment'],
            'content': content,
            'user_id': session['user_id'],
            'photo_id': photo_id,
            'created_at': datetime.utcnow()
        })
        next_id['comment'] += 1
        flash('Comment added!', 'success')
    return redirect(url_for('photo_detail', photo_id=photo_id))

# ==================== BOOKING MANAGEMENT ====================

@app.route('/booking/create', methods=['GET', 'POST'])
def create_booking():
    """Create new booking request"""
    if request.method == 'POST':
        bookings.append({
            'id': next_id['booking'],
            'client_name': request.form.get('name'),
            'client_email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'service_type': request.form.get('service'),
            'booking_date': datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            'message': request.form.get('message', ''),
            'status': 'pending',
            'user_id': session.get('user_id'),
            'created_at': datetime.utcnow()
        })
        next_id['booking'] += 1
        flash('Booking submitted successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_booking.html')

@app.route('/booking/manage')
@admin_required
def manage_bookings():
    """Admin: View and manage all bookings"""
    return render_template('admin/manage_bookings.html', 
                          bookings=sorted(bookings, key=lambda x: x['created_at'], reverse=True))


@app.route('/booking/update/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking(booking_id):
    """Admin: Update booking status"""
    booking = next((b for b in bookings if b['id'] == booking_id), None)
    if booking:
        status = request.form.get('status')
        if status in ['pending', 'confirmed', 'cancelled', 'completed']:
            booking['status'] = status
            flash('Booking updated!', 'success')
    return redirect(url_for('manage_bookings'))

@app.route('/booking/delete/<int:booking_id>', methods=['POST'])
@admin_required
def delete_booking(booking_id):
    """Admin: Delete booking"""
    global bookings
    bookings = [b for b in bookings if b['id'] != booking_id]
    flash('Booking deleted!', 'success')
    return redirect(url_for('manage_bookings'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@admin_required
def admin():
    """Admin panel - view contacts and manage system"""
    return render_template('admin/dashboard.html', 
                          contacts=contacts,
                          messages=contacts,  # Alias for compatibility
                          stats={'users': len(users), 'photos': len(photos), 
                                'bookings': len(bookings), 'contacts': len(contacts)})


@app.route('/admin/users')
@admin_required
def manage_users():
    """Admin: Manage all users"""
    return render_template('admin/manage_users.html', 
                          users=sorted(users, key=lambda x: x['created_at'], reverse=True))


@app.route('/admin/user/toggle-role/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_role(user_id):
    """Admin: Toggle user role between admin/user"""
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        user['role'] = 'admin' if user['role'] == 'user' else 'user'
        flash(f'Role updated to {user["role"]}!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Admin: Delete user account"""
    global users
    if user_id != session['user_id']:
        users = [u for u in users if u['id'] != user_id]
        flash('User deleted!', 'success')
    else:
        flash('Cannot delete yourself!', 'danger')
    return redirect(url_for('manage_users'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)