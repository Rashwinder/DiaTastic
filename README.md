# Diatastic
Master Data Science Capstone Unit
Contributors:

* [@caobaichuan1122](https://github.com/caobaichuan1122)
* [@luckwei](https://github.com/luckwei)
* Arun Khurana
* Shiwei Xu

<h2>
Purpose
</h2>

*Diatastic was created to assist diabetics in managing their diabetes by unifying the various tools that were currently available. The backend was built in Django, and any data used is stored in an SQL database. The flow of information starts with the user entering the individual items that they consumed, as well as their blood sugar level. A recommended insulin dose is then provided. Diatastic also provides the user with visualisations of their blood sugar level, carbohydrate intake and insulin usage over time. In addition, the visualisations can be sent to an email of the user's choice.*

<h2>
  Core Functionalities
</h2>

<h3>
  Diary.
</h3>

<p align="center">
  <img src="https://user-images.githubusercontent.com/110654543/208659115-4be8df43-afb1-4c97-bb3c-1d05e1c04f82.png"/>
</p>

The core functionality behind the website is the diary. The user is able to select items that they consumed through three dependent dropdowns, along with an add-to-cart functionality. This emulates the individual ingredients to an entire meal. When the entry is submitted, the user is provided with a recommended insulin dose.

<h3>
  Metrics.
</h3>

<p align="center">
  <img src="https://user-images.githubusercontent.com/110654543/208660736-ea1cbf59-5615-4b60-bb17-6b9e50db2cc5.png"/>
</p>

This is where the user views their blood sugar level, carbohydrate intake and insulin usage over time, with the option of filtering it down to a specific time period. In addition, the user has the option of sending these same visualisations to an email address of their choice, preferably their endocrinologist.

<h3>
  Email.
</h3>
<p align="center">
  <img src="https://user-images.githubusercontent.com/110654543/208662437-19ff2897-61a7-429d-ab08-1fea767190de.png"/>
</p>

The only information the user has to input in this form is the email address. The subject and message information is pre-determined and cannot be changed.
