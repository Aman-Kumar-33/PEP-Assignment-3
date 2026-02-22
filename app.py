import json
import os
from flask import Flask, render_template, request, redirect, url_for
from collections import Counter

app = Flask(__name__)
DATA_FILE = 'data.json'

# --- HELPER FUNCTIONS ---
def load_data():
    """Reads the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {"users": [], "stalls": [], "menu_items": [], "orders": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    """Writes back to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- STUDENT ROUTES ---
@app.route('/')
def home():
    data = load_data()
    # Get only active stalls
    active_stalls = [s for s in data.get('stalls', []) if s.get('is_active')]
    return render_template('index.html', stalls=active_stalls)

@app.route('/menu/<int:stall_id>')
def menu(stall_id):
    data = load_data()
    
    # Find the specific stall
    stall = next((s for s in data['stalls'] if s['id'] == stall_id), None)
    if not stall:
        return "Stall not found!"
        
    # Find menu items for this stall
    items = [item for item in data['menu_items'] if item['stall_id'] == stall_id and item['is_available']]
    
    return render_template('menu.html', stall=stall, items=items)

@app.route('/place_order', methods=['POST'])
def place_order():
    data = load_data()
    
    user_id = int(request.form.get('user_id', 1))
    stall_id = int(request.form.get('stall_id'))
    time_slot = request.form.get('time_slot')
    
    # Generate a new Order ID
    new_order_id = max([o['id'] for o in data['orders']] + [0]) + 1
    
    # Gather the specific items ordered
    ordered_items = []
    for key, value in request.form.items():
        if key.startswith('item_') and int(value) > 0:
            item_id = int(key.split('_')[1])
            # Find the item name for easy displaying later
            item_info = next((i for i in data['menu_items'] if i['id'] == item_id), None)
            if item_info:
                ordered_items.append({
                    "item_id": item_id,
                    "item_name": item_info['item_name'],
                    "quantity": int(value)
                })
    
    # Create the order record
    new_order = {
        "id": new_order_id,
        "user_id": user_id,
        "stall_id": stall_id,
        "time_slot": time_slot,
        "status": "Pending",
        "items": ordered_items
    }
    
    # Save it to the JSON file
    data['orders'].append(new_order)
    save_data(data)
    
    return render_template('success.html', order_id=new_order_id, time_slot=time_slot)


# --- STALL ADMIN ROUTES ---
@app.route('/manage/<int:stall_id>')
def manage_stall(stall_id):
    data = load_data()
    stall = next((s for s in data['stalls'] if s['id'] == stall_id), None)
    menu_items = [item for item in data['menu_items'] if item['stall_id'] == stall_id]
    
    # Format the live orders so the HTML template can read them easily
    live_orders = []
    for order in reversed(data['orders']): # reversed so newest is on top
        if order['stall_id'] == stall_id and order['status'] != 'Completed':
            # Get the student's name
            student = next((u for u in data['users'] if u['id'] == order['user_id']), {"name": "Unknown"})
            
            # Format "Samosa (x2), Chai (x1)"
            summary = ", ".join([f"{item['item_name']} (x{item['quantity']})" for item in order['items']])
            
            live_orders.append({
                "id": order['id'],
                "student_name": student['name'],
                "order_summary": summary,
                "time_slot": order['time_slot'],
                "status": order['status']
            })
            
    return render_template('manage_stall.html', stall=stall, menu_items=menu_items, live_orders=live_orders)

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    data = load_data()
    stall_id = int(request.form.get('stall_id'))
    
    new_item_id = max([i['id'] for i in data['menu_items']] + [0]) + 1
    
    new_item = {
        "id": new_item_id,
        "stall_id": stall_id,
        "item_name": request.form.get('item_name'),
        "price": float(request.form.get('price')),
        "is_available": True
    }
    
    data['menu_items'].append(new_item)
    save_data(data)
    
    return redirect(url_for('manage_stall', stall_id=stall_id))

@app.route('/update_status', methods=['POST'])
def update_status():
    data = load_data()
    order_id = int(request.form.get('order_id'))
    new_status = request.form.get('status')
    stall_id = int(request.form.get('stall_id'))
    
    # Find the order and update its status
    for order in data['orders']:
        if order['id'] == order_id:
            order['status'] = new_status
            break
            
    save_data(data)
    return redirect(url_for('manage_stall', stall_id=stall_id))

@app.route('/my_orders/<int:user_id>')
def my_orders(user_id):
    data = load_data()
    
    # Safely get orders and order_details using .get() so it never crashes!
    all_orders = data.get('orders', [])
    all_details = data.get('order_details', [])
    all_stalls = data.get('stalls', [])
    all_menu_items = data.get('menu_items', [])
    
    # 1. Find all orders for this specific user
    user_orders = [o for o in all_orders if o.get('user_id') == user_id]
    
    display_orders = []
    for order in user_orders:
        # 2. Get the Stall Name
        stall = next((s for s in all_stalls if s.get('id') == order.get('stall_id')), None)
        stall_name = stall['stall_name'] if stall else "Unknown Stall"
        
        # 3. Get the Items Summary (e.g., "Samosa (x2)")
        details = [d for d in all_details if d.get('order_id') == order.get('id')]
        item_summary = []
        for d in details:
            item = next((i for i in all_menu_items if i.get('id') == d.get('menu_item_id')), None)
            if item:
                item_summary.append(f"{item['item_name']} (x{d['quantity']})")
                
        # 4. Package it up for the HTML template
        display_orders.append({
            "id": order.get('id'),
            "stall_name": stall_name,
            "time_slot": order.get('time_slot'),
            "status": order.get('status', 'Pending'),
            "items": ", ".join(item_summary)
        })
        
    # Sort so the newest orders appear at the top
    display_orders.reverse() 
    
    return render_template('my_orders.html', orders=display_orders)
# --- ANALYTICS ROUTE ---
@app.route('/analytics')
def analytics():
    data = load_data()
    
    # Count how many orders happen in each time slot using Python's Counter
    time_slots = [order['time_slot'] for order in data['orders']]
    slot_counts = Counter(time_slots)
    
    # Format for Chart.js
    peak_data = [{"time_slot": slot, "order_count": count} for slot, count in slot_counts.items()]
    
    # Sort them alphabetically (e.g., 10:00 AM comes before 12:30 PM)
    peak_data = sorted(peak_data, key=lambda x: x['time_slot'])
    
    return render_template('analytics.html', peak_data=peak_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)