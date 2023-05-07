import streamlit as st
import requests as rq
import pandas as pd
import numpy as np
import bs4 as bs
import os

def get_data_from_web():
    url = "http://vinomikulcik.cz"
    page = rq.get(url)

    soup = bs.BeautifulSoup(page.text, "lxml")

    tables = soup.findAll("table")

    data = []
    for each in tables:
        for i in each.find_all("tr"):
            title = i.text
            data.append(title)

    for item in data:
        if " nabídka vín " in item:
            data.remove(item)

    nlst = []
    for e in data:
        nlst.append(e.split("\n"))

    nlst = [list(filter(None, lst)) for lst in nlst]

    lst1 = []
    lst2 = []
    for a in nlst[::2]:
        lst1.append(a)

    for b in nlst[1::2]:
        lst2.append(b)

    res = []
    for i,j in zip(lst1, lst2):
        res.append(i + j)

    df = pd.DataFrame(res, columns=["ID", "Name", "Pct", "Price", "Description"])
    df = df.fillna(np.NaN)
    df = df.dropna()
    return df

DATA = "data.csv"

st.set_page_config(layout="wide")

st.title("Víno Mikulčík")
st.subheader("jmikulcik@seznam.cz")

btn = st.button("Get actual selection")

if btn:
    res = get_data_from_web()
    res.to_csv(DATA, header=True, index=False)

if os.path.isfile(DATA):
    df = pd.read_csv(DATA)
    df["Price"] = df["Price"].str.replace(",-", "")
    df["Count"] = 0
    
    c, cc = st.columns([3,1])
    with c:
        editable_df = st.experimental_data_editor(df, key="data", use_container_width=True)

    ndf = editable_df.where(editable_df["Count"] > 0)
    ndf = ndf[["Count", "Price", "ID"]]
    ndf = ndf.dropna()
    ndf["Count"] = ndf["Count"].astype("int")
    ndf["Price"] = ndf["Price"].astype("int")

    st.markdown("**Order list:**")
    for index, row in ndf.iterrows():
        st.markdown(str(row["Count"]) + " x " + row["ID"])

    sumval = (ndf["Count"] * ndf["Price"]).sum()
    countval = ndf["Count"].sum()
    st.markdown("Total count: **" + str(countval) + "**")
    st.markdown("Total sum: **" + str(sumval) + "** Kč")

    # edited_df = st.experimental_data_editor(df, key="dftable")
    # st.write(st.session_state["dftable"])

    # for index, row in df.iterrows():
    #     print(row.T)
    #     st.dataframe(row, use_container_width=True)
    #     c1, c2, c3, c4 = st.columns([1,1,1,20])
    #     with c1:
    #         add = st.button("Add", key="btnadd"+str(index), use_container_width=True)
    #         if add:
    #             x = int(st.session_state[str("counter"+str(index))])
    #             st.session_state[str("counter"+str(index))] = str(x + 1)
    #     with c2:
    #         rem = st.button("Remove", key="btnrem"+str(index), use_container_width=True)
    #         if rem:
    #             x = int(st.session_state[str("counter"+str(index))])
    #             st.session_state[str("counter"+str(index))] = str(x - 1)
    #     with c3:
    #         val = st.text_input("Count", 0, key="counter"+str(index), label_visibility="collapsed")
else:
    st.write("No data found")
