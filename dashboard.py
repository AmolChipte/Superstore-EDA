import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.figure_factory as ff
import warnings
warnings.filterwarnings('ignore')

# Intialize Web Page
st.set_page_config(page_title="Super Store !!!", page_icon=":bar_chart:",layout="wide")
st.title(":bar_chart: SuperStore EDA")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

# ---------- Import CSV File ----------
fl = st.file_uploader(":file_folder: Upload a File", type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1",)

# ---------- Dashboard Date ----------
col1, col2 = st.columns(2)
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")

# Getting Min and Max from Date Column
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# ---------- Filter Data using Sidebar ----------
# Create for Region
st.sidebar.header("Choose your Filter: ")
region = st.sidebar.multiselect("Pick your Region: ", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create for State
state = st.sidebar.multiselect("Pick your State: ", df["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Create for City
city = st.sidebar.multiselect("Pick your City: ", df["City"].unique())

# Filter Data Using State, Region and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

# ---------- Data Visualization ----------
# Category Wise Sales - Bar Graph
with col1:
    st.subheader("Category Wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
    template= "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

# Region Wise Sales - Pie Chart
with col2:
    st.subheader("Region Wise Sales")
    fig = px.pie(filtered_df, values= "Sales", names="Region", hole=0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
# Category View Data
with cl1:
    with st.expander("Category View Data"):
        # st.write(category_df.style.background_gradient(cmap="Blues"))
        st.write(category_df)
        csv = category_df.to_csv(index = False).encode("UTF-8")
        st.download_button("Download Data", data = csv, file_name="Category.csv", mime="text/csv",
                           help="Click Here to Download Data as CSV File")

# Region View Data
with cl2:
    with st.expander("Region View Data"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        # st.write(region.style.background_gradient(cmap="Oranges"))
        st.write(region)
        csv = region.to_csv(index = False).encode("UTF-8")
        st.download_button("Download Data", data = csv, file_name="Region.csv", mime="text/csv",
                           help="Click Here to Download Data as CSV File")

# ---------- Time Series Analysis ----------
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y = "Sales", labels={"Sales": "Amount"}, height = 500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Time Series:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("UTF-8")
    st.download_button("Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv",
                       help="Click Here to Download Data as CSV File")

# ---------- Tree Map ----------
# Create a Tree Map Based on Region, Category and Sub Category
st.subheader("Hierarchical View of Sales using Tree Map")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values="Sales",hover_data=["Sales"],color="Sub-Category")
fig3.update_layout(width= 800, height= 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)
with chart1:
    st.subheader("Segment Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text= filtered_df["Segment"], textposition= "inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Category Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text= filtered_df["Category"], textposition= "inside")
    st.plotly_chart(fig, use_container_width=True)
# ---------- Month Wise Sub Category Sales Summary ----------
st.subheader(":point_right: Month Wise Sub_category Sales Summary")
with st.expander("Summary Table"):
    df_sample = df[0:5][["Region","State","City","Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month Wise Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data= filtered_df, values= "Sales", index = ["Sub-Category"], columns = "month")
    st.write(sub_category_year)

# --------- Relation Between Sales and Profit - Scatter Plot ---------
data1 = px.scatter(filtered_df, x = "Sales", y= "Profit", size= "Quantity")
data1['layout'].update(title= "Relationship Between Sales and Profit using Scatter Plot",
                       xaxis= dict(title="Sales"),
                       yaxis= dict(title="Profit"))
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    # st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))
    st.write(filtered_df.iloc[:500, 1:20:2])

# ---------- Download Original Dataset ----------
csv = df.to_csv(index= False).encode('UTF-8')
st.download_button("Download Data", data = csv, file_name = "Data.csv", mime= "text/csv")