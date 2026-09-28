import streamlit as st
from datetime import datetime, date
import pandas as pd
import base64

st.set_page_config(
    page_title="Royal Taste VIP POS",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- STYLE ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
.stApp {
    background: linear-gradient(135deg,#080b12,#111827 55%,#080b12);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#080b12,#151b28);
}
.vip { color:#d4af37; font-family:"Playfair Display",serif; }
.hero {
    padding:32px; border-radius:24px; margin-bottom:24px;
    background: linear-gradient(90deg,rgba(0,0,0,.88),rgba(0,0,0,.45)),
    url("https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1600&q=80");
    background-size:cover; background-position:center;
    border:1px solid rgba(212,175,55,.4);
}
.hero h1 { color:white; font-family:"Playfair Display",serif; font-size:44px; }
.card {
    background:#111827; border:1px solid rgba(212,175,55,.22);
    border-radius:18px; padding:15px; margin-bottom:15px;
}
.section {
    color:white; font-family:"Playfair Display",serif;
    font-size:28px; border-left:4px solid #d4af37;
    padding-left:12px; margin:20px 0;
}
.price { color:#d4af37; font-size:20px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION DATA ----------
defaults = {
    "cart": [],
    "orders": [],
    "customers": [],
    "expenses": [],
    "stock": [],
    "order_no": 1001,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, list) else value

# ---------- MENU ----------
MENU = [
    {"id":1,"name":"Royal Zinger Burger","cat":"Burgers","price":650,
     "img":"https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80"},
    {"id":2,"name":"Classic Beef Burger","cat":"Burgers","price":750,
     "img":"https://images.unsplash.com/photo-1565299507177-b0ac66763828?auto=format&fit=crop&w=800&q=80"},
    {"id":3,"name":"Margherita Pizza","cat":"Pizza","price":1100,
     "img":"https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=800&q=80"},
    {"id":4,"name":"Pepperoni Pizza","cat":"Pizza","price":1450,
     "img":"https://images.unsplash.com/photo-1628840042765-356cda07504e?auto=format&fit=crop&w=800&q=80"},
    {"id":5,"name":"Chicken Shawarma","cat":"Shawarma","price":350,
     "img":"https://images.unsplash.com/photo-1529006557810-274b9b2fc783?auto=format&fit=crop&w=800&q=80"},
    {"id":6,"name":"Loaded French Fries","cat":"Fries","price":450,
     "img":"https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=800&q=80"},
    {"id":7,"name":"Crispy Fried Chicken","cat":"Chicken","price":850,
     "img":"https://images.unsplash.com/photo-1562967916-eb82221dfb36?auto=format&fit=crop&w=800&q=80"},
    {"id":8,"name":"Chicken Biryani","cat":"Rice","price":450,
     "img":"https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=800&q=80"},
    {"id":9,"name":"Chicken BBQ Platter","cat":"BBQ","price":1350,
     "img":"https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80"},
    {"id":10,"name":"Club Sandwich","cat":"Sandwiches","price":700,
     "img":"https://images.unsplash.com/photo-1553909489-cd47e0907980?auto=format&fit=crop&w=800&q=80"},
    {"id":11,"name":"Fresh Lemonade","cat":"Drinks","price":250,
     "img":"https://images.unsplash.com/photo-1621263764928-df1444c5e859?auto=format&fit=crop&w=800&q=80"},
    {"id":12,"name":"Cold Coffee","cat":"Drinks","price":350,
     "img":"https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=800&q=80"},
    {"id":13,"name":"Chocolate Cake","cat":"Desserts","price":400,
     "img":"https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80"},
    {"id":14,"name":"Cheesecake","cat":"Desserts","price":500,
     "img":"https://images.unsplash.com/photo-1565958011703-44f9829ba187?auto=format&fit=crop&w=800&q=80"},
]

def rs(n):
    return f"Rs. {n:,.0f}"

def add_item(item):
    for x in st.session_state.cart:
        if x["id"] == item["id"]:
            x["qty"] += 1
            return
    st.session_state.cart.append({
        "id": item["id"], "name": item["name"],
        "price": item["price"], "qty": 1
    })

def subtotal():
    return sum(x["price"] * x["qty"] for x in st.session_state.cart)

def bill_html(order):
    rows = "".join(
        f"<tr><td>{x['name']}</td><td>{x['qty']}</td>"
        f"<td>Rs. {x['price']:,.0f}</td>"
        f"<td>Rs. {x['price']*x['qty']:,.0f}</td></tr>"
        for x in order["items"]
    )
    return f"""<!doctype html><html><head><title>Royal Taste Invoice</title>
    <style>
    body{{font-family:Arial;width:80mm;margin:auto;color:#111}}
    h2,.center{{text-align:center}} table{{width:100%;border-collapse:collapse;font-size:12px}}
    th,td{{padding:5px 2px;border-bottom:1px dashed #888}}
    .total{{font-size:18px;font-weight:bold}}
    </style></head><body>
    <h2>ROYAL TASTE</h2><div class="center">HOTEL & RESTAURANT</div><hr>
    Order #: {order['no']}<br>Date: {order['date']}<br>
    Customer: {order['customer']}<br>Type: {order['type']}<br><br>
    <table><tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr>
    {rows}</table><br>
    Subtotal: Rs. {order['subtotal']:,.0f}<br>
    Discount: Rs. {order['discount']:,.0f}<br>
    Tax: Rs. {order['tax']:,.0f}<br>
    Service: Rs. {order['service']:,.0f}<br>
    <p class="total">GRAND TOTAL: Rs. {order['total']:,.0f}</p>
    Payment: {order['payment']}<hr>
    <div class="center">Thank you!<br>Prepared by Mazhar Abbas</div>
    <script>window.onload=function(){{window.print()}}</script>
    </body></html>"""

def print_link(html, filename):
    data = base64.b64encode(html.encode()).decode()
    return f'<a href="data:text/html;base64,{data}" download="{filename}" target="_blank" style="display:inline-block;padding:10px 18px;background:#d4af37;color:#000;text-decoration:none;border-radius:8px;font-weight:bold;">🖨️ OPEN / PRINT BILL</a>'

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("<div style='text-align:center;font-size:55px'>👑</div>", unsafe_allow_html=True)
    st.markdown("<h2 class='vip' style='text-align:center'>ROYAL TASTE</h2>", unsafe_allow_html=True)
    st.caption("VIP HOTEL POS")
    page = st.radio("MENU", [
        "🏠 Dashboard","🛒 POS / New Order","🍽️ Menu","🪑 Tables",
        "👨‍🍳 Kitchen","🚚 Delivery","👥 Customers","📦 Inventory",
        "💰 Expenses","👨‍💼 Employees","📊 Reports","🏨 Hotel Rooms","⚙️ Settings"
    ])
    st.divider()
    st.caption("Prepared by Mazhar Abbas")

# ---------- DASHBOARD ----------
if page == "🏠 Dashboard":
    st.markdown("<div class='hero'><div class='vip' style='font-size:42px'>ROYAL TASTE</div><h1>VIP Hotel & Restaurant POS</h1><p>Complete Restaurant • Fast Food • Hotel Management</p></div>", unsafe_allow_html=True)
    sales = sum(o["total"] for o in st.session_state.orders)
    expenses = sum(x["amount"] for x in st.session_state.expenses)
    a,b,c,d = st.columns(4)
    a.metric("Today's Sales", rs(sales))
    b.metric("Orders", len(st.session_state.orders))
    c.metric("Customers", len(st.session_state.customers))
    d.metric("Expenses", rs(expenses))
    st.markdown("<div class='section'>Recent Orders</div>", unsafe_allow_html=True)
    if st.session_state.orders:
        st.dataframe(pd.DataFrame(st.session_state.orders)[["no","date","customer","type","payment","total","status"]], use_container_width=True, hide_index=True)
    else:
        st.info("No orders yet.")

# ---------- POS ----------
elif page == "🛒 POS / New Order":
    st.markdown("<div class='section'>🛒 New Order</div>", unsafe_allow_html=True)
    a,b,c = st.columns(3)
    order_type = a.selectbox("Order Type", ["Dine-In","Takeaway","Delivery","Room Service"])
    table = b.selectbox("Table", [f"Table {i:02d}" for i in range(1,21)])
    customer = c.text_input("Customer Name", "Walk-in Customer")

    search = st.text_input("🔎 Search Food")
    cats = ["All"] + sorted(set(x["cat"] for x in MENU))
    cat = st.selectbox("Category", cats)
    items = [x for x in MENU if cat == "All" or x["cat"] == cat]
    if search:
        items = [x for x in items if search.lower() in x["name"].lower()]

    cols = st.columns(3)
    for i,item in enumerate(items):
        with cols[i%3]:
            st.markdown(f"""<div class='card'>
            <img src="{item['img']}" style="width:100%;height:175px;object-fit:cover;border-radius:12px">
            <h4>{item['name']}</h4><div class='price'>{rs(item['price'])}</div></div>""", unsafe_allow_html=True)
            if st.button(f"➕ Add {item['name']}", key=f"add_{item['id']}", use_container_width=True):
                add_item(item)
                st.rerun()

    st.markdown("<div class='section'>🛒 Cart & Checkout</div>", unsafe_allow_html=True)
    if not st.session_state.cart:
        st.info("Cart is empty.")
    else:
        for i,item in enumerate(st.session_state.cart):
            a,b,c,d = st.columns([4,1,2,1])
            a.write(item["name"])
            item["qty"] = b.number_input("Qty", 1, 99, item["qty"], key=f"q{i}")
            c.write(rs(item["price"]*item["qty"]))
            if d.button("❌", key=f"del{i}"):
                st.session_state.cart.pop(i)
                st.rerun()

        sub = subtotal()
        a,b,c = st.columns(3)
        discount = a.number_input("Discount Rs.", min_value=0.0)
        tax_pct = b.number_input("Tax %", min_value=0.0, value=5.0)
        service_pct = c.number_input("Service %", min_value=0.0, value=5.0)
        tax = max(0,(sub-discount)*tax_pct/100)
        service = max(0,(sub-discount)*service_pct/100)
        total = sub-discount+tax+service

        a,b,c,d = st.columns(4)
        a.metric("Subtotal",rs(sub)); b.metric("Discount",rs(discount))
        c.metric("Tax + Service",rs(tax+service)); d.metric("Grand Total",rs(total))
        payment = st.selectbox("Payment",["Cash","Card","JazzCash","EasyPaisa","Bank Transfer","Split Payment"])
        note = st.text_area("Order Note")
        if st.button("✅ COMPLETE ORDER", type="primary", use_container_width=True):
            no = st.session_state.order_no
            st.session_state.order_no += 1
            order = {
                "no":no,"date":datetime.now().strftime("%Y-%m-%d %H:%M"),
                "customer":customer,"type":order_type,
                "table":table,"items":[x.copy() for x in st.session_state.cart],
                "subtotal":sub,"discount":discount,"tax":tax,"service":service,
                "total":total,"payment":payment,"note":note,"status":"Completed"
            }
            st.session_state.orders.append(order)
            if customer != "Walk-in Customer":
                st.session_state.customers.append({"name":customer,"phone":"","date":str(date.today())})
            st.session_state.cart = []
            html = bill_html(order)
            st.success(f"Order #{no} completed.")
            st.markdown(print_link(html,f"RoyalTaste_Order_{no}.html"), unsafe_allow_html=True)

# ---------- MENU ----------
elif page == "🍽️ Menu":
    st.markdown("<div class='section'>🍽️ Premium Food Menu</div>", unsafe_allow_html=True)
    search = st.text_input("Search")
    data = [x for x in MENU if not search or search.lower() in x["name"].lower()]
    for item in data:
        a,b,c,d = st.columns([1,4,2,1])
        a.image(item["img"], width=90)
        b.write(f"**{item['name']}**")
        b.caption(item["cat"])
        c.markdown(f"<div class='price'>{rs(item['price'])}</div>", unsafe_allow_html=True)
        if d.button("Add", key=f"m{item['id']}"):
            add_item(item); st.toast("Added to cart")

# ---------- TABLES ----------
elif page == "🪑 Tables":
    st.markdown("<div class='section'>🪑 Table Management</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i in range(1,21):
        status = "Reserved" if i % 5 == 0 else "Available"
        with cols[(i-1)%4]:
            if status == "Available": st.success(f"🟢 Table {i:02d}\n\nAvailable")
            else: st.warning(f"🟡 Table {i:02d}\n\nReserved")
            st.button(f"Select Table {i:02d}", key=f"t{i}")

# ---------- KITCHEN ----------
elif page == "👨‍🍳 Kitchen":
    st.markdown("<div class='section'>👨‍🍳 Kitchen Display</div>", unsafe_allow_html=True)
    if not st.session_state.orders:
        st.info("No orders.")
    for o in reversed(st.session_state.orders):
        with st.expander(f"Order #{o['no']} • {o['type']} • {o['status']}"):
            for x in o["items"]:
                st.write(f"🍽️ {x['name']} × {x['qty']}")
            a,b,c = st.columns(3)
            if a.button("Preparing",key=f"p{o['no']}"): o["status"]="Preparing"; st.rerun()
            if b.button("Ready",key=f"r{o['no']}"): o["status"]="Ready"; st.rerun()
            if c.button("Served",key=f"s{o['no']}"): o["status"]="Served"; st.rerun()

# ---------- DELIVERY ----------
elif page == "🚚 Delivery":
    st.markdown("<div class='section'>🚚 Delivery</div>", unsafe_allow_html=True)
    orders = [o for o in st.session_state.orders if o["type"]=="Delivery"]
    if not orders: st.info("No delivery orders.")
    for o in orders:
        st.info(f"Order #{o['no']} • {o['customer']} • {rs(o['total'])}")
        st.text_input("Address", key=f"a{o['no']}")
        st.selectbox("Rider",["Rider 01","Rider 02","Rider 03"],key=f"rider{o['no']}")

# ---------- CUSTOMERS ----------
elif page == "👥 Customers":
    st.markdown("<div class='section'>👥 Customers</div>", unsafe_allow_html=True)
    with st.form("customer"):
        n=st.text_input("Name"); p=st.text_input("Phone"); ad=st.text_area("Address")
        if st.form_submit_button("Save Customer") and n:
            st.session_state.customers.append({"name":n,"phone":p,"address":ad,"date":str(date.today())})
            st.success("Saved.")
    if st.session_state.customers: st.dataframe(pd.DataFrame(st.session_state.customers),use_container_width=True,hide_index=True)

# ---------- INVENTORY ----------
elif page == "📦 Inventory":
    st.markdown("<div class='section'>📦 Inventory</div>", unsafe_allow_html=True)
    with st.form("stock"):
        n=st.text_input("Item"); q=st.number_input("Quantity",min_value=0.0); u=st.selectbox("Unit",["KG","Litre","Piece","Packet","Box"]); s=st.text_input("Supplier")
        if st.form_submit_button("Add Stock") and n:
            st.session_state.stock.append({"Item":n,"Quantity":q,"Unit":u,"Supplier":s,"Date":str(date.today())})
            st.success("Stock added.")
    if st.session_state.stock: st.dataframe(pd.DataFrame(st.session_state.stock),use_container_width=True,hide_index=True)

# ---------- EXPENSES ----------
elif page == "💰 Expenses":
    st.markdown("<div class='section'>💰 Expenses</div>", unsafe_allow_html=True)
    with st.form("expense"):
        n=st.text_input("Expense"); amount=st.number_input("Amount",min_value=0.0); cat=st.selectbox("Category",["Food Purchase","Electricity","Gas","Rent","Salary","Maintenance","Other"])
        if st.form_submit_button("Save Expense") and n:
            st.session_state.expenses.append({"title":n,"amount":amount,"category":cat,"date":str(date.today())})
            st.success("Saved.")
    if st.session_state.expenses: st.dataframe(pd.DataFrame(st.session_state.expenses),use_container_width=True,hide_index=True)

# ---------- EMPLOYEES ----------
elif page == "👨‍💼 Employees":
    st.markdown("<div class='section'>👨‍💼 Employees & Roles</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        ["Admin","Administrator","Active"],["Cashier 01","Cashier","Active"],
        ["Waiter 01","Waiter","Active"],["Chef 01","Kitchen","Active"],["Rider 01","Delivery","Active"]
    ],columns=["Name","Role","Status"]),use_container_width=True,hide_index=True)

# ---------- REPORTS ----------
elif page == "📊 Reports":
    st.markdown("<div class='section'>📊 Reports</div>", unsafe_allow_html=True)
    if not st.session_state.orders:
        st.info("No sales data.")
    else:
        df=pd.DataFrame(st.session_state.orders)
        a,b,c,d=st.columns(4)
        a.metric("Sales",rs(df["total"].sum())); b.metric("Orders",len(df))
        c.metric("Average",rs(df["total"].mean())); d.metric("Customers",len(st.session_state.customers))
        st.dataframe(df[["no","date","customer","type","payment","total","status"]],use_container_width=True,hide_index=True)
        st.bar_chart(df.groupby("payment")["total"].sum())
        st.download_button("⬇️ Download CSV",df.to_csv(index=False),"sales.csv","text/csv")

# ---------- HOTEL ----------
elif page == "🏨 Hotel Rooms":
    st.markdown("<div class='section'>🏨 Hotel Rooms</div>", unsafe_allow_html=True)
    rooms=[]
    for i in range(1,21):
        rooms.append({
            "Room":str(100+i),
            "Type":"Deluxe" if i%2 else "Executive",
            "Price":8500 if i%2 else 12000,
            "Status":"Occupied" if i%6==0 else ("Reserved" if i%4==0 else "Available")
        })
    df=pd.DataFrame(rooms)
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.metric("Available Rooms",len(df[df["Status"]=="Available"]))
    guest=st.text_input("Guest Name")
    room=st.selectbox("Room",df["Room"].tolist())
    if st.button("🏨 Check-in / Save Booking"): st.success(f"Booking saved: {guest} • Room {room}")

# ---------- SETTINGS ----------
elif page == "⚙️ Settings":
    st.markdown("<div class='section'>⚙️ Settings</div>", unsafe_allow_html=True)
    st.text_input("Hotel / Restaurant Name","ROYAL TASTE HOTEL & RESTAURANT")
    st.text_input("Phone","+92 300 0000000")
    st.text_input("Address","Karachi, Pakistan")
    st.number_input("Tax %",value=5.0)
    st.selectbox("Currency",["PKR - Rs.","USD - $","AED - د.إ"])
    st.success("Settings panel ready.")

st.markdown("<hr><div style='text-align:center;color:#777;padding:15px'>ROYAL TASTE VIP POS<br><b style='color:#d4af37'>Prepared by Mazhar Abbas</b></div>",unsafe_allow_html=True)
