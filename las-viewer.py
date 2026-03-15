# app.py

import streamlit as st
import laspy
import numpy as np
import pyvista as pv
import tempfile

st.title("LiDAR LAS Viewer")

uploaded_file = st.file_uploader("Upload a .LAS file", type=["las"])

if uploaded_file is not None:

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.write("Loading LAS file...")

    las = laspy.read(tmp_path)

    # Create point array
    points = np.vstack((las.x, las.y, las.z)).T

    # Downsample large files
    MAX_POINTS = 2_000_000
    if len(points) > MAX_POINTS:
        idx = np.random.choice(len(points), MAX_POINTS, replace=False)
        points = points[idx]
        z = las.z[idx]
    else:
        z = las.z

    cloud = pv.PolyData(points)
    cloud["Z"] = z

    st.write(f"Points visualized: {len(points):,}")

    plotter = pv.Plotter(off_screen=True)
    plotter.add_points(
        cloud,
        scalars="Z",
        point_size=2,
        render_points_as_spheres=True
    )

    html_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False).name
    plotter.export_html(html_file)

    st.success("Rendering complete")

    # Display inside Streamlit
    with open(html_file, "r") as f:
        html = f.read()

    st.components.v1.html(html, height=800, scrolling=False)
