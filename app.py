from flask import Flask, jsonify, render_template, request
from db_config import get_db_connection

app = Flask(__name__)

@app.route('/')
def home():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed!"
    
    cursor = conn.cursor(dictionary=True) 
    
    try:
        cursor.execute("SELECT id, stall_name, owner_name FROM stalls WHERE is_active = TRUE")
        stalls = cursor.fetchall() 
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        cursor.close()
        conn.close()
    
    return render_template('index.html', stalls=stalls)
# Add this new route below your home route
@app.route('/menu/<int:stall_id>')
def menu(stall_id):
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed!"
    
    cursor = conn.cursor(dictionary=True) 
    
    try:
        cursor.execute("SELECT * FROM stalls WHERE id = %s", (stall_id,))
        stall = cursor.fetchone() 
        
        cursor.execute("SELECT * FROM menu_items WHERE stall_id = %s AND is_available = TRUE", (stall_id,))
        items = cursor.fetchall()
        
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        cursor.close()
        conn.close()
    
    
    return render_template('menu.html', stall=stall, items=items)
@app.route('/place_order', methods=['POST'])
def place_order():
    
    user_id = request.form.get('user_id')
    stall_id = request.form.get('stall_id')
    time_slot = request.form.get('time_slot')
    
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed!"
    
    cursor = conn.cursor()
    
    try:
        
        order_query = "INSERT INTO orders (user_id, stall_id, time_slot, status) VALUES (%s, %s, %s, 'Pending')"
        cursor.execute(order_query, (user_id, stall_id, time_slot))
        
        order_id = cursor.lastrowid 
        
        
        for key, value in request.form.items():
            
            if key.startswith('item_') and int(value) > 0:
                item_id = int(key.split('_')[1]) 
                quantity = int(value)
                
                
                detail_query = "INSERT INTO order_details (order_id, menu_item_id, quantity) VALUES (%s, %s, %s)"
                cursor.execute(detail_query, (order_id, item_id, quantity))
        
        
        conn.commit()
        
    except Exception as e:
        conn.rollback() 
        return f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()
        
    
    return render_template('success.html', order_id=order_id, time_slot=time_slot)
from flask import redirect, url_for

@app.route('/manage/<int:stall_id>')
def manage_stall(stall_id):
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed!"
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        
        cursor.execute("SELECT * FROM stalls WHERE id = %s", (stall_id,))
        stall = cursor.fetchone()
        
        
        cursor.execute("SELECT * FROM menu_items WHERE stall_id = %s", (stall_id,))
        menu_items = cursor.fetchall()
        
        
        order_query = """
            SELECT o.id, u.name as student_name, o.time_slot, o.status, 
                   GROUP_CONCAT(CONCAT(m.item_name, ' (x', od.quantity, ')') SEPARATOR ', ') as order_summary
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN order_details od ON o.id = od.order_id
            JOIN menu_items m ON od.menu_item_id = m.id
            WHERE o.stall_id = %s AND o.status != 'Completed'
            GROUP BY o.id
            ORDER BY o.id DESC
        """
        cursor.execute(order_query, (stall_id,))
        live_orders = cursor.fetchall()
        
    except Exception as e:
        return f"Error: {e}"
    finally:
        cursor.close()
        conn.close()
        
    return render_template('manage_stall.html', stall=stall, menu_items=menu_items, live_orders=live_orders)

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    stall_id = request.form.get('stall_id')
    item_name = request.form.get('item_name')
    price = request.form.get('price')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO menu_items (stall_id, item_name, price) VALUES (%s, %s, %s)", 
                       (stall_id, item_name, price))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('manage_stall', stall_id=stall_id))

@app.route('/update_status', methods=['POST'])
def update_status():
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')
    stall_id = request.form.get('stall_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('manage_stall', stall_id=stall_id))
@app.route('/analytics')
def analytics():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed!"
    
    cursor = conn.cursor(dictionary=True)
    try:
        
        cursor.execute("""
            SELECT time_slot, COUNT(id) as order_count 
            FROM orders 
            GROUP BY time_slot 
            ORDER BY time_slot
        """)
        peak_data = cursor.fetchall()
        
    except Exception as e:
        return f"Error: {e}"
    finally:
        cursor.close()
        conn.close()
        
    return render_template('analytics.html', peak_data=peak_data)
if __name__ == '__main__':
    app.run(debug=True, port=5000)