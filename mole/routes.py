from flask import render_template, flash, redirect, url_for, request
from mole import app, db
from mole.forms import LoginForm, RegistrationForm, CrimeForm
from mole.models import User, Crime
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime, time, timedelta
import plotly.graph_objs as go


@app.route("/")
@app.route("/index")
@login_required
def index():
    user = {"username": "Sibabalwe"}
    return render_template("index.html", title="Home Page", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


# @app.route("/report_crime", methods=["POST"])
# def report_crime():
#     crime_type = request.form["crime_type"]
#     location = request.form["location"]
#     day_of_week = request.form["day_of_week"]
#     hour = request.form["hour"]
#     minute = request.form["minute"]

#     # Combine the hour and minute into a single string, and parse it as a time
#     time_str = f"{hour}:{minute}"
#     time = datetime.strptime(time_str, "%H:%M").time()

#     # Create a new Crime object and add it to the database
#     crime = Crime(
#         type=crime_type, location=location, day_of_week=day_of_week, time=time
#     )
#     db.session.add(crime)
#     db.session.commit()

#     # Redirect the user back to the form page
#     return redirect(url_for("crime_form"))


@app.route("/report_crime", methods=["GET", "POST"])
def report_crime():
    form = CrimeForm()
    if form.validate_on_submit():
        # Create a datetime object with the date set to today and time set to the form data
        crime_time = time(hour=form.hour.data, minute=form.minute.data, second=0)
        crime_datetime = datetime.combine(datetime.today(), crime_time)

        # Create a new Crime object with the form data
        crime = Crime(
            type=form.crime_type.data,
            location=form.location.data,
            day_of_week=form.day_of_week.data,
            time=crime_datetime,
        )
        db.session.add(crime)
        db.session.commit()
        flash("Crime submitted successfully!", "success")
        return redirect(url_for("report_crime"))
    return render_template("report_crime.html", title="Submit a Crime", form=form)


@app.route("/recent-crimes")
def recent_crimes():
    # Get crimes that happened in the last 7 days
    today = datetime.today().date()
    last_week = today - timedelta(days=7)
    crimes = Crime.query.filter(Crime.time >= last_week).all()

    # Count the frequency of each crime type
    crime_types = [crime.type for crime in crimes]
    crime_counts = {
        crime_type: crime_types.count(crime_type) for crime_type in set(crime_types)
    }

    # Create a bar graph using Plotly
    fig = go.Figure(
        data=[go.Bar(x=list(crime_counts.keys()), y=list(crime_counts.values()))],
        layout=go.Layout(
            title=go.layout.Title(text="Recent Crime Types"),
            xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text="Crime Type")),
            yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text="Frequency")),
        ),
    )

    graph = fig.to_html(full_html=False)

    return render_template("recent_crimes.html", title="Recent Crimes", graph=graph)
