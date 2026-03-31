import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="GardenROI Tracker", page_icon="🌱", layout="wide")
st.title("🌱 GardenROI Tracker - with Varieties")
st.caption("Track inputs • Varieties • Break-even & ROI by location")

VARIETIES = {
    "Tomatoes": ["Cherry (Sungold)", "Cherry (Black Cherry)", "Cherry (Sweet Million)", "Roma (San Marzano)", "Roma (Plum Regal)", "Beefsteak (Brandywine)", "Beefsteak (Cherokee Purple)", "Better Boy", "Early Girl", "Other"],
    "Cucumbers": ["Slicing (Marketmore)", "Slicing (Straight Eight)", "Pickling (Boston Pickling)", "Other"],
    "Bell Peppers": ["California Wonder", "Red Knight", "Orange Bell", "Yellow Bell", "Other"],
    "Zucchini": ["Black Beauty", "Genovese", "Yellow (Golden)", "Other"],
    "Green Beans": ["Bush (Provider)", "Pole (Kentucky Wonder)", "Other"],
    "Carrots": ["Nantes", "Imperator", "Baby", "Rainbow", "Other"],
    "Lettuce": ["Romaine", "Butterhead", "Leaf (Red/Green)", "Iceberg", "Other"],
    "Potatoes": ["Russet", "Red Pontiac", "Yukon Gold", "Fingerling", "Other"],
    "Onions": ["Yellow", "Red", "White", "Sweet (Vidalia-type)", "Other"],
    "Peas": ["Sugar Snap", "Snow Peas", "Shelling", "Other"],
    "Radishes": ["Cherry Belle", "French Breakfast", "Daikon", "Other"],
    "Broccoli": ["Green Magic", "Purple Sprouting", "Other"],
    "Spinach": ["Bloomsdale", "Baby Leaf", "Malabar (climbing)", "Other"],
    "Kale": ["Curly (Lacinato)", "Red Russian", "Dinosaur", "Other"],
    "Corn": ["Sweet (Silver Queen)", "Sweet (Golden Bantam)", "Other"]
}

TOP_PLANTS = list(VARIETIES.keys())

DEFAULT_PRICES = {
    "Tomatoes": 1.60, "Cucumbers": 1.50, "Bell Peppers": 1.80, "Zucchini": 1.20,
    "Green Beans": 2.80, "Carrots": 1.35, "Lettuce": 2.00, "Potatoes": 0.90,
    "Onions": 1.15, "Peas": 3.00, "Radishes": 2.50, "Broccoli": 1.80,
    "Spinach": 3.50, "Kale": 3.20, "Corn": 0.80
}

if "shared_costs" not in st.session_state:
    st.session_state.shared_costs = pd.DataFrame(columns=["Date", "Description", "Cost"])
if "crops" not in st.session_state:
    st.session_state.crops = pd.DataFrame(columns=["Plant_Variety", "Num_Plants", "Seed_Cost", "Other_Cost", "Actual_Yield_lb", "Price_per_lb"])

st.sidebar.header("Your Garden")
location = st.sidebar.text_input("Location (City, State)", "Oakville, Missouri")

st.header("Top 15 Plants with Popular Varieties")
st.write("Select plant + variety below.")

tab1, tab2, tab3 = st.tabs(["📋 Shared Inputs & Costs", "🌾 Crop Tracking", "📊 Break-even & ROI"])

with tab1:
    st.subheader("Shared Garden Costs (fence, barriers, soil, etc.)")
    edited_shared = st.data_editor(
        st.session_state.shared_costs,
        num_rows="dynamic",
        use_container_width=True,
        column_config={"Date": st.column_config.DateColumn(default=datetime.today().date()), "Cost": st.column_config.NumberColumn(min_value=0.0, format="$%.2f")}
    )
    st.session_state.shared_costs = edited_shared
    total_shared = st.session_state.shared_costs["Cost"].sum() if not st.session_state.shared_costs.empty else 0.0
    st.metric("Total Shared Costs", f"${total_shared:,.2f}")

with tab2:
    st.subheader("Add / Edit Crops with Varieties")
    col1, col2 = st.columns([1, 1])
    with col1:
        plant = st.selectbox("Plant", TOP_PLANTS)
        variety = st.selectbox("Variety", VARIETIES[plant])
        full_name = f"{plant} - {variety}" if variety != "Other" else plant
        num_plants = st.number_input("Number of plants / row-feet", min_value=1, value=10)
    with col2:
        seed_cost = st.number_input("Seed / transplant cost ($)", min_value=0.0, value=5.0)
        other_cost = st.number_input("Other crop-specific costs ($)", min_value=0.0, value=0.0)
        yield_lb = st.number_input("Actual harvested yield (lbs)", min_value=0.0, value=20.0)

    default_price = DEFAULT_PRICES.get(plant, 1.50)
    price_per_lb = st.number_input("Local price per lb ($)", min_value=0.01, value=default_price, step=0.01, help=f"National avg for {plant} near Oakville, MO. Adjust for local prices.")

    if st.button("➕ Add/Update Crop"):
        new_row = pd.DataFrame([{"Plant_Variety": full_name, "Num_Plants": num_plants, "Seed_Cost": seed_cost, "Other_Cost": other_cost, "Actual_Yield_lb": yield_lb, "Price_per_lb": price_per_lb}])
        st.session_state.crops = pd.concat([st.session_state.crops, new_row], ignore_index=True)

    st.subheader("Your Crops")
    if not st.session_state.crops.empty:
        edited_crops = st.data_editor(st.session_state.crops, num_rows="dynamic", use_container_width=True, column_config={"Price_per_lb": st.column_config.NumberColumn(format="$%.2f")})
        st.session_state.crops = edited_crops

with tab3:
    st.subheader(f"Financials for {location}")
    total_shared = st.session_state.shared_costs["Cost"].sum() if not st.session_state.shared_costs.empty else 0.0
    crops_df = st.session_state.crops.copy()

    if not crops_df.empty:
        crops_df["Revenue"] = crops_df["Actual_Yield_lb"] * crops_df["Price_per_lb"]
        crops_df["Crop_Cost"] = crops_df["Seed_Cost"] + crops_df["Other_Cost"]
        total_crop_cost = crops_df["Crop_Cost"].sum()
        total_revenue = crops_df["Revenue"].sum()
        total_cost = total_shared + total_crop_cost

        if total_cost > 0:
            break_even_revenue = total_cost
            if total_revenue > 0:
                multiplier = break_even_revenue / total_revenue
            else:
                multiplier = None
            crops_df["BreakEven_Yield_lb"] = crops_df.apply(lambda row: row["Crop_Cost"] / row["Price_per_lb"] if row["Price_per_lb"] > 0 else 0, axis=1)

        st.dataframe(crops_df.style.format({"Seed_Cost": "${:.2f}", "Other_Cost": "${:.2f}", "Actual_Yield_lb": "{:.1f} lb", "Price_per_lb": "${:.2f}", "Revenue": "${:.2f}", "Crop_Cost": "${:.2f}", "BreakEven_Yield_lb": "{:.1f} lb"}), use_container_width=True)

        colA, colB, colC = st.columns(3)
        with colA: st.metric("Total Costs", f"${total_cost:,.2f}")
        with colB: st.metric("Total Revenue", f"${total_revenue:,.2f}")
        with colC: 
            roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
            st.metric("ROI", f"{roi:.1f}%")

        st.subheader("Break-even Summary")
        st.write(f"You need **${break_even_revenue:,.2f}** in produce value to break even.")
        if total_revenue > 0 and multiplier:
            st.write(f"At current yields, you are **{multiplier:.2f}x** your break-even target.")

        if st.button("💾 Download all data as CSV"):
            csv = pd.concat([st.session_state.shared_costs.assign(Type="Shared"), crops_df.assign(Type="Crop")], ignore_index=True).to_csv(index=False)
            st.download_button("Download CSV", csv, f"garden_data_{datetime.today().date()}.csv", "text/csv")
    else:
        st.info("Add crops in the Crop Tracking tab!")

st.caption("Built for Connor in Oakville, MO • Free to use & share")
