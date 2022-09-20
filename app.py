import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import streamlit as st
import re

hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
st.markdown(hide_table_row_index, unsafe_allow_html=True)            

st.markdown("<h1 style='text-align: center'>Choose my car</h1>", unsafe_allow_html=True)
st.text("Have trouble selecting a car from the list of cars? We can help you.")
url_input_form = st.form("url_input_form", clear_on_submit=True)
url = url_input_form.text_input("Paste cars.com URL")
submit_button = url_input_form.form_submit_button(label='Submit', )

if submit_button:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    cars = soup.find_all("div", class_="vehicle-card")
    year_all = []
    mileage_all = []
    price_all = []
    name_all = []
    url_all = []
    for car in cars:
        url = car.find(href=re.compile("/vehicledetail.+?/"), class_="vehicle-card-link")
        year = int(car.find("h2", class_="title").text.strip()[0:5])
        mileage = int(car.find("div", class_="mileage").text.strip()[0:-3].replace(',',''))
        if car.find("span", class_="primary-price").text.strip() == "Not Priced":
            price = 0
        else:
            price = int(car.find("span", class_="primary-price").text.strip()[1:].replace(',',''))
        name = car.find("h2", class_="title").text.strip()
        year_all.append(year)
        mileage_all.append(mileage)
        price_all.append(price)
        name_all.append(name)
        url_all.append("https://www.cars.com" + url['href'])
    data = pd.DataFrame({"year":year_all, "mileage":mileage_all, "price": price_all, "name": name_all, "url": url_all})
    data = data[data["price"] > 0]
    data["year_rank"] = data["year"].rank()
    data["mileage_rank"] = data["mileage"].rank(ascending=False)
    data["price_rank"] = data["price"].rank(ascending=False)
    data["avg_rank"] = round((data["year_rank"] + data["mileage_rank"] + data["price_rank"])/3)
    data.drop(columns=["year_rank", "mileage_rank", "price_rank"], inplace=True)
    data.sort_values(by=["avg_rank", "price"], ascending=[False, True], inplace=True)
    st.table(data.drop(columns=["avg_rank", "url"]))