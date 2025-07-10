from flask import Flask, render_template, request, redirect, session, url_for
import os
from werkzeug.utils import secure_filename
from utils.db import init_db, add_user, verify_user,\
                     add_artwork, get_all_artworks,\
                     add_to_cart, get_cart_items, clear_cart

app = Flask(__name__)
app.secret_key = 'artsecret'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize persistent SQLite database
init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role     = request.form['role']
        if add_user(username, password, role):
            return redirect('/login')
        else:
            return "Username already exists", 400
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = verify_user(request.form['username'], request.form['password'])
        if u:
            session['user_id']  = u['id']
            session['username'] = u['username']
            session['role']     = u['role']
            return redirect('/dashboard')
        else:
            return "Login failed", 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template(
      'dashboard.html',
      username=session['username'],
      role=session['role']
    )

@app.route('/upload', methods=['GET','POST'])
def upload():
    if 'user_id' not in session or session['role']!='artist':
        return redirect('/login')
    if request.method=='POST':
        f        = request.files['image']
        title    = request.form['title']
        desc     = request.form['description']
        price    = float(request.form['price'])
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        add_artwork(session['user_id'], title, desc, price, filename)
        return redirect('/dashboard')
    return render_template('upload.html')

@app.route('/browse')
def browse():
    arts = get_all_artworks()
    return render_template('browse.html', artworks=arts)

@app.route('/add_to_cart/<int:art_id>')
def cart_add(art_id):
    if 'user_id' not in session or session['role']!='buyer':
        return redirect('/login')
    add_to_cart(session['user_id'], art_id)
    return redirect('/cart')

@app.route('/cart')
def cart_view():
    if 'user_id' not in session or session['role']!='buyer':
        return redirect('/login')
    items = get_cart_items(session['user_id'])
    total = sum(item['price'] for item in items)
    return render_template('cart.html', items=items, total=total)

# Combined checkout GET (show form) and POST (process order)
@app.route('/checkout', methods=['GET','POST'])
def checkout():
    if 'user_id' not in session or session['role']!='buyer':
        return redirect('/login')
    if request.method == 'POST':
        # process submitted form
        name    = request.form['name']
        phone   = request.form['phone']
        address = request.form['address']
        pincode = request.form['pincode']
        payment = request.form['payment']
        clear_cart(session['user_id'])
        return render_template(
          'checkout_success.html',
          name=name, phone=phone,
          address=address, pincode=pincode,
          payment=payment
        )
    # GET => show checkout form
    return render_template('checkout.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True, port=8000)
