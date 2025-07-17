from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.file1 import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime

main_bp = Blueprint('main', __name__)

def admin_required(f):
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Login required.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@main_bp.route('/', methods=['GET'])
def home():
    return render_template('login.html')

@main_bp.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    lots = ParkingLot.query.all()
    users = User.query.filter(User.role=='user').all()
    print(f"DEBUG: Admin dashboard fetching users: {[u.username for u in users]}")
    return render_template('admin_dashboard.html', lots=lots, users=users)

@main_bp.route('/user/dashboard', methods=['GET'])
@login_required
def user_dashboard():
    lots = ParkingLot.query.all()
    reservations = Reservation.query.filter_by(user_id=session['user_id']).all()
    return render_template('user_dashboard.html', lots=lots, reservations=reservations)

# Admin: Add parking lot
@main_bp.route('/admin/lot/add', methods=['GET', 'POST'])
@admin_required
def add_lot():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['max_spots'])
        lot = ParkingLot(name=name, price=price, address=address, pin_code=pin_code, max_spots=max_spots)
        db.session.add(lot)
        db.session.commit()
        # Create spots
        for _ in range(max_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)
        db.session.commit()
        flash('Parking lot added.')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('parking_lots.html', action='add')

# Admin: Edit parking lot
@main_bp.route('/admin/lot/edit/<int:lot_id>', methods=['GET', 'POST'])
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.name = request.form['name']
        lot.price = float(request.form['price'])
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        new_max_spots = int(request.form['max_spots'])
        current_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        occupied_spots = [spot for spot in current_spots if spot.status == 'O']
        available_spots = [spot for spot in current_spots if spot.status == 'A']
        if new_max_spots < len(occupied_spots):
            flash(f'Cannot reduce max spots below the number of occupied spots ({len(occupied_spots)}).')
            return render_template('parking_lots.html', lot=lot, action='edit')
        if new_max_spots > len(current_spots):
            # Add new spots
            for _ in range(new_max_spots - len(current_spots)):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
        elif new_max_spots < len(current_spots):
            # Remove available spots first
            spots_to_remove = available_spots[:len(current_spots) - new_max_spots]
            for spot in spots_to_remove:
                db.session.delete(spot)
        lot.max_spots = new_max_spots
        db.session.commit()
        flash('Parking lot updated.')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('parking_lots.html', lot=lot, action='edit')

# Admin: Delete parking lot (only if all spots are available)
@main_bp.route('/admin/lot/delete/<int:lot_id>', methods=['POST'])
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    if occupied > 0:
        flash('Cannot delete lot with occupied spots.')
    else:
        db.session.delete(lot)
        db.session.commit()
        flash('Parking lot deleted.')
    return redirect(url_for('main.admin_dashboard'))

# Admin: View parking spots in a lot
@main_bp.route('/admin/lot/<int:lot_id>/spots')
@admin_required
def view_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
    return render_template('parking_spots.html', lot=lot, spots=spots)

# User: Reserve a spot (first available in selected lot)
@main_bp.route('/user/reserve/<int:lot_id>', methods=['POST'])
@login_required
def reserve_spot(lot_id):
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        flash('No available spots in this lot.')
        return redirect(url_for('main.user_dashboard'))
    spot.status = 'O'
    reservation = Reservation(spot_id=spot.id, user_id=session['user_id'], parking_timestamp=datetime.utcnow())
    db.session.add(reservation)
    db.session.commit()
    flash('Spot reserved!')
    return redirect(url_for('main.user_dashboard'))

# User: Release a spot
@main_bp.route('/user/release/<int:reservation_id>', methods=['POST'])
@login_required
def release_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != session['user_id']:
        flash('Unauthorized.')
        return redirect(url_for('main.user_dashboard'))
    if reservation.leaving_timestamp:
        flash('Spot already released.')
        return redirect(url_for('main.user_dashboard'))
    reservation.leaving_timestamp = datetime.utcnow()
    # Calculate cost (simple: price * hours)
    hours = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
    spot = ParkingSpot.query.get(reservation.spot_id)
    lot = ParkingLot.query.get(spot.lot_id)
    reservation.cost = round(hours * lot.price, 2)
    spot.status = 'A'
    db.session.commit()
    flash(f'Spot released. Total cost: ₹{reservation.cost}')
    return redirect(url_for('main.user_dashboard'))

# Admin: Force Release a spot
@main_bp.route('/admin/force_release/<int:reservation_id>', methods=['POST'])
@admin_required
def admin_force_release(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.leaving_timestamp:
        flash('Spot is already released.')
        return redirect(url_for('main.admin_dashboard'))

    reservation.leaving_timestamp = datetime.utcnow()
    # Calculate cost (simple: price * hours)
    hours = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
    spot = ParkingSpot.query.get(reservation.spot_id)
    lot = ParkingLot.query.get(spot.lot_id)
    reservation.cost = round(hours * lot.price, 2)
    spot.status = 'A'
    db.session.commit()
    flash(f'Spot ID {spot.id} (Lot {lot.name}) force released. Cost: ₹{reservation.cost}')
    return redirect(url_for('main.admin_dashboard')) 