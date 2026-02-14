from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photography.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ==================== DATABASE MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    photos = db.relationship('Photo', backref='photographer', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to comments
    comments = db.relationship('Comment', backref='photo', lazy=True, cascade='all, delete-orphan')


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    service_type = db.Column(db.String(50), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='comments')


# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'danger')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== ROUTES ====================

@app.route('/')
def index():
    featured_photos = Photo.query.order_by(Photo.views.desc()).limit(6).all()
    return render_template('index.html', photos=featured_photos)


@app.route('/portfolio')
def portfolio():
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    
    query = Photo.query
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Photo.title.contains(search) | Photo.description.contains(search))
    
    photos = query.order_by(Photo.created_at.desc()).all()
    categories = db.session.query(Photo.category).distinct().all()
    
    return render_template('portfolio.html', photos=photos, categories=categories, 
                         selected_category=category, search_query=search)


@app.route('/gallery')
def gallery():
    photos = Photo.query.order_by(Photo.created_at.desc()).all()
    return render_template('gallery.html', photos=photos)


@app.route('/photo/<int:photo_id>')
def photo_detail(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo.views += 1
    db.session.commit()
    
    comments = Comment.query.filter_by(photo_id=photo_id).order_by(Comment.created_at.desc()).all()
    return render_template('photo_detail.html', photo=photo, comments=comments)


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/about')
def about():
    stats = {
        'total_photos': Photo.query.count(),
        'total_clients': User.query.filter_by(role='user').count(),
        'total_bookings': Booking.query.count(),
        'completed_projects': Booking.query.filter_by(status='completed').count()
    }
    return render_template('about.html', stats=stats)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # Here you would typically send an email
        flash('Thank you for contacting us! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(name=name, email=email, phone=phone)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ==================== USER DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    if user.role == 'admin':
        stats = {
            'total_users': User.query.count(),
            'total_photos': Photo.query.count(),
            'pending_bookings': Booking.query.filter_by(status='pending').count(),
            'total_views': db.session.query(db.func.sum(Photo.views)).scalar() or 0
        }
        recent_photos = Photo.query.order_by(Photo.created_at.desc()).limit(5).all()
        recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    else:
        stats = {
            'my_photos': Photo.query.filter_by(user_id=user.id).count(),
            'my_bookings': Booking.query.filter_by(user_id=user.id).count(),
            'total_views': db.session.query(db.func.sum(Photo.views)).filter(Photo.user_id == user.id).scalar() or 0,
            'total_likes': db.session.query(db.func.sum(Photo.likes)).filter(Photo.user_id == user.id).scalar() or 0
        }
        recent_photos = Photo.query.filter_by(user_id=user.id).order_by(Photo.created_at.desc()).limit(5).all()
        recent_bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', user=user, stats=stats, 
                         recent_photos=recent_photos, recent_bookings=recent_bookings)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.phone = request.form.get('phone')
        
        new_password = request.form.get('new_password')
        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return redirect(url_for('profile'))
            user.set_password(new_password)
        
        db.session.commit()
        session['user_name'] = user.name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('auth/profile.html', user=user)


# ==================== PHOTO MANAGEMENT (CRUD) ====================

@app.route('/photo/upload', methods=['GET', 'POST'])
@login_required
def upload_photo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        
        if 'photo' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('upload_photo'))
        
        file = request.files['photo']
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('upload_photo'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to make it unique
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            photo = Photo(
                title=title,
                description=description,
                filename=filename,
                category=category,
                user_id=session['user_id']
            )
            
            db.session.add(photo)
            db.session.commit()
            
            flash('Photo uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file type. Only PNG, JPG, JPEG, and GIF are allowed.', 'danger')
    
    return render_template('upload_photo.html')


@app.route('/photo/edit/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def edit_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    
    # Check if user owns the photo or is admin
    if photo.user_id != session['user_id'] and session.get('user_role') != 'admin':
        flash('You do not have permission to edit this photo.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        photo.title = request.form.get('title')
        photo.description = request.form.get('description')
        photo.category = request.form.get('category')
        
        db.session.commit()
        flash('Photo updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_photo.html', photo=photo)


@app.route('/photo/delete/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    
    # Check if user owns the photo or is admin
    if photo.user_id != session['user_id'] and session.get('user_role') != 'admin':
        flash('You do not have permission to delete this photo.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Delete file from filesystem
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))
    except:
        pass
    
    db.session.delete(photo)
    db.session.commit()
    
    flash('Photo deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/photo/like/<int:photo_id>', methods=['POST'])
@login_required
def like_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo.likes += 1
    db.session.commit()
    return jsonify({'success': True, 'likes': photo.likes})


# ==================== BOOKING MANAGEMENT ====================

@app.route('/booking/create', methods=['GET', 'POST'])
def create_booking():
    if request.method == 'POST':
        client_name = request.form.get('name')
        client_email = request.form.get('email')
        phone = request.form.get('phone')
        service_type = request.form.get('service')
        booking_date_str = request.form.get('date')
        message = request.form.get('message')
        
        try:
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d')
        except:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('create_booking'))
        
        booking = Booking(
            client_name=client_name,
            client_email=client_email,
            phone=phone,
            service_type=service_type,
            booking_date=booking_date,
            message=message,
            user_id=session.get('user_id')
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking request submitted successfully! We will contact you soon.', 'success')
        return redirect(url_for('index'))
    
    return render_template('create_booking.html')


@app.route('/booking/manage')
@admin_required
def manage_bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('manage_bookings.html', bookings=bookings)


@app.route('/booking/update/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    status = request.form.get('status')
    
    if status in ['pending', 'confirmed', 'cancelled', 'completed']:
        booking.status = status
        db.session.commit()
        flash('Booking status updated!', 'success')
    
    return redirect(url_for('manage_bookings'))


@app.route('/booking/delete/<int:booking_id>', methods=['POST'])
@admin_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted!', 'success')
    return redirect(url_for('manage_bookings'))


# ==================== ADMIN PANEL ====================

@app.route('/admin/users')
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('manage_users.html', users=users)


@app.route('/admin/user/toggle-role/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_role(user_id):
    user = User.query.get_or_404(user_id)
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    flash(f'User role updated to {user.role}!', 'success')
    return redirect(url_for('manage_users'))


@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('manage_users'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted!', 'success')
    return redirect(url_for('manage_users'))


# ==================== COMMENTS ====================

@app.route('/photo/<int:photo_id>/comment', methods=['POST'])
@login_required
def add_comment(photo_id):
    content = request.form.get('content')
    
    if not content:
        flash('Comment cannot be empty.', 'danger')
        return redirect(url_for('photo_detail', photo_id=photo_id))
    
    comment = Comment(
        content=content,
        user_id=session['user_id'],
        photo_id=photo_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added!', 'success')
    return redirect(url_for('photo_detail', photo_id=photo_id))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# ==================== INITIALIZE DATABASE ====================

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@photo.com').first()
        if not admin:
            admin = User(
                name='Admin User',
                email='admin@photo.com',
                phone='+1234567890',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: admin@photo.com / admin123')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    