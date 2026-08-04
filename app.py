import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Page Setup
st.set_page_config(page_title="Visual Board Nesting Software", layout="wide")

st.title("🪚 Visual Panel Cutting & Nesting Optimizer")
st.write("පහත Chart එකෙන් ඔයාගේ Panel List එක සහ Board Details සරලව වෙනස් කර **'Generate Nesting Plan'** ක්ලික් කරන්න.")

st.markdown("---")

# ==========================================
# 1. VISUAL CONTROLS (BOARD & BLADE SETTINGS)
# ==========================================
st.sidebar.header("⚙️ Master Board Settings")

sheet_w = st.sidebar.number_input("Board Length / දිග (mm)", value=2440, step=100)
sheet_h = st.sidebar.number_input("Board Width / පළල (mm)", value=1830, step=100)
kerf = st.sidebar.number_input("Blade Saw Thickness / Saw Gap (mm)", value=4, step=1)

st.sidebar.info("💡 **Tip:** Standard Boards: 2440×1830 mm (8×6) or 2440×1220 mm (8×4)")

# ==========================================
# 2. INTERACTIVE DATA TABLE (NO CODE NEEDED)
# ==========================================
st.subheader("📋 Panel List Input Table")
st.caption("පහත Table එකේ පේළි මත Click කර Diga, Palala, Qty, Wood Grain (Rotate) ඕනෑම කෙනෙකුට වෙනස් කළ හැක.")

# Default data set with clear headers
default_panels = pd.DataFrame([
    {"Panel Name": "Top Panel", "Thickness (mm)": "25mm", "Length (mm)": 2345, "Width (mm)": 400, "Qty": 1, "Allow Rotate (No Wood Grain)": False},
    {"Panel Name": "Door I", "Thickness (mm)": "18mm", "Length (mm)": 2319, "Width (mm)": 386, "Qty": 6, "Allow Rotate (No Wood Grain)": False},
    {"Panel Name": "Side Wall", "Thickness (mm)": "15mm", "Length (mm)": 1955, "Width (mm)": 375, "Qty": 3, "Allow Rotate (No Wood Grain)": False},
    {"Panel Name": "Shelf", "Thickness (mm)": "15mm", "Length (mm)": 370, "Width (mm)": 347, "Qty": 8, "Allow Rotate (No Wood Grain)": True},
    {"Panel Name": "Bottom Strip", "Thickness (mm)": "18mm", "Length (mm)": 1095, "Width (mm)": 80, "Qty": 6, "Allow Rotate (No Wood Grain)": False},
])

# Interactive Data Table Widget
edited_df = st.data_editor(
    default_panels, 
    num_rows="dynamic", 
    use_container_width=True
)

# ==========================================
# 3. NESTING ENGINE LOGIC
# ==========================================
def run_2d_nesting(df, sheet_w, sheet_h, kerf):
    boards = []
    current_board = []
    curr_x, curr_y = 0, 0
    max_row_h = 0

    # Expand pieces by Qty
    all_pieces = []
    for _, row in df.iterrows():
        try:
            qty = int(row["Qty"])
            for _ in range(qty):
                all_pieces.append({
                    "name": str(row["Panel Name"]),
                    "thick": str(row["Thickness (mm)"]),
                    "w": float(row["Width (mm)"]),
                    "h": float(row["Length (mm)"]),
                    "rotate": bool(row["Allow Rotate (No Wood Grain)"])
                })
        except (ValueError, KeyError):
            continue

    # Sort largest area first
    all_pieces.sort(key=lambda p: p["w"] * p["h"], reverse=True)

    for p in all_pieces:
        w, h = p["w"], p["h"]

        # Handle Wood Grain Rotation if allowed
        if p["rotate"] and (curr_x + w > sheet_w) and (curr_x + h <= sheet_w):
            w, h = h, w

        # New Row Check
        if curr_x + w > sheet_w:
            curr_x = 0
            curr_y += max_row_h + kerf
            max_row_h = 0

        # New Board Check
        if curr_y + h > sheet_h:
            boards.append(current_board)
            current_board = []
            curr_x, curr_y = 0, 0
            max_row_h = 0

        # Place piece
        current_board.append({
            "name": p["name"],
            "thick": p["thick"],
            "x": curr_x,
            "y": curr_y,
            "w": w,
            "h": h
        })

        curr_x += w + kerf
        if h > max_row_h:
            max_row_h = h

    if current_board:
        boards.append(current_board)

    return boards

# ==========================================
# 4. RUN & GENERATE VISUAL BLUEPRINTS
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🚀 RUN NESTING PLAN (Visuals හදන්න)", type="primary", use_container_width=True):
    
    boards = run_2d_nesting(edited_df, sheet_w, sheet_h, kerf)
    
    st.success(f"🎯 Nesting Complete! Total Master Boards Needed: **{len(boards)} Board(s)**")
    st.markdown("---")

    # Render Visual Cutting Pattern for each Board
    for idx, board in enumerate(boards, 1):
        st.subheader(f"📐 Master Board #{idx} ({sheet_w} mm × {sheet_h} mm)")
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Draw Master Board Outline
        ax.add_patch(patches.Rectangle((0, 0), sheet_w, sheet_h, facecolor='#f8fafc', edgecolor='#1a365d', linewidth=2.5))

        colors = ['#ebf8ff', '#feebc8', '#c6f6d5', '#e9d8fd', '#fed7d7', '#e2e8f0']

        for p_idx, p in enumerate(board):
            color = colors[p_idx % len(colors)]
            # Draw individual cut panel
            ax.add_patch(patches.Rectangle((p["x"], p["y"]), p["w"], p["h"], facecolor=color, edgecolor='#2b6cb0', linewidth=1.5))
            
            # Label
            label_text = f"{p['name']}\n({p['thick']})\n{p['h']}×{p['w']} mm"
            ax.text(
                p["x"] + p["w"]/2, p["y"] + p["h"]/2, 
                label_text, 
                color='#1a365d', weight='bold', fontsize=8,
                ha='center', va='center'
            )

        plt.xlim(-50, sheet_w + 50)
        plt.ylim(-50, sheet_h + 50)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.title(f"Board Pattern #{idx} Visual Layout", fontsize=11, fontweight='bold', color='#1a365d')
        plt.xlabel("Width (mm)")
        plt.ylabel("Length (mm)")
        
        st.pyplot(fig)
        st.markdown("---")
