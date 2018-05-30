#
#
#
#
import os
import operator
import secrets

from datetime import datetime
from urllib.parse import urlparse
from PIL import Image

import flask
from flask import render_template, url_for, flash, redirect, request
from main import app, db, bcrypt
from main.forms import RegistrationForm, LoginForm, ProfileForm, ChangeProfilePicForm, ChangeUserForm, ChangePasswordForm, MacroForm, MealForm, AddExerciseForm, WorkoutForm

from main.models import User, Profile, Schedule, Exercise, Macros, Meal
from flask_login import login_user, current_user, logout_user, login_required


# Route to the homepage.
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


# Route to the user's fitness page.
@app.route("/my-fitness-page", methods = ['GET', 'POST'])
def fitness_page():
    return render_template('fitness-page.html', title = 'My Fitness Page')


### Routes and functions to do with the workouts page. ###

#
@app.route("/workouts")
def workouts():
    day = datetime.strftime(datetime.now(), "%A")

    workout = Schedule.query.filter(Schedule.user_id == current_user.id, Schedule.day_of_week == day).first().workout

    exercises = Exercise.query.filter(Exercise.user_id == current_user.id, Exercise.day == day).all()

    return render_template('workouts.html', title = 'Workouts', today = day, workout = workout, exercises = exercises)


@app.route("/workouts/today/update-workout", methods = ['GET', 'POST'])
@login_required
def update_workout1():
    day = datetime.strftime(datetime.now(), "%A")
    form = WorkoutForm()

    if form.validate_on_submit():
        workout = Schedule.query.filter(Schedule.user_id == current_user.id, Schedule.day_of_week == day).first()
        label = workout.workout

        if form.reset.data == True:
            exercises = Exercise.query.filter(Exercise.user_id == current_user.id, Exercise.day == day).all()

            for exercise in exercises:
                db.session.delete(exercise)

        workout.workout = form.workout.data

        db.session.commit()

        return redirect(url_for('workouts'))    

    elif request.method == 'GET':
        form.day.data = day

    return render_template('change-workout.html', title = "Change Workout", form = form)


#
@app.route("/workouts/view-schedule")
def view_schedule():

    schedules = Schedule.query.filter(Schedule.user_id == current_user.id).all()

    return render_template('view-schedule.html', title = 'Workout Schedules', schedules = schedules)


@app.route("/workouts/add-exercise", methods = ['GET', 'POST'])
@login_required
def add_exercise1():

    form = AddExerciseForm()

    if form.validate_on_submit():
        user_id = current_user.id
        day = form.day.data
        workout = Schedule.query.filter(Schedule.user_id == user_id, Schedule.day_of_week == day).first().workout

        if workout == "None Set.":
            flash("Please set a workout for that day first.", "danger")
            return redirect(url_for('workouts'))

        if form.difficulty.data == None:
            difficulty = "None Given"

        else:
            difficulty = form.difficulty.data

        exercise = Exercise(name = form.name.data, day = form.day.data, workout = workout, num_sets = form.num_sets.data,
            num_reps = form.num_reps.data, difficulty = difficulty, user_id = user_id)

        db.session.add(exercise)
        db.session.commit()

        return redirect(url_for('workouts'))

    return render_template('new-exercise.html', title = "Add Exercise", form = form)



### Routes and functions to do with the nutrition page. ###

"""."""
def get_remaining_macros(macros, todays_meals):
    macros = macros
    todays_meals = todays_meals

    remaining_macros = [macros[0].protein - sum([x.protein for x in todays_meals]),
                        macros[0].carbs - sum([x.carbs for x in todays_meals]),
                        macros[0].fat - sum([x.fat for x in todays_meals]),
                        macros[0].calories - sum([x.calories for x in todays_meals])]

    return remaining_macros


# Route to the main nutrition page.
@app.route("/nutrition", methods = ['GET', 'POST'])
def nutrition():
    today = datetime.today()

    if current_user.is_authenticated:
        macros = Macros.query.filter(Macros.user_id == current_user.id).all()
        meals = Meal.query.filter(Meal.user_id == current_user.id).all()
        todays_meals = [x for x in meals if x.time.strftime('%d-%m-%Y') == today.strftime('%d-%m-%Y')]

        remaining = get_remaining_macros(macros, todays_meals)

        return render_template('nutrition.html', title = 'Nutrition', macros = macros, remaining = remaining, meals = todays_meals,
            today = datetime.today())

    else:
        return render_template('nutrition.html', title = 'Nutrition', today = datetime.today())


#
@app.route("/nutrition/set-macros", methods = ['GET', 'POST'])
@login_required
def set_macros():
    form = MacroForm()

    if form.validate_on_submit():

        calories = 4*form.protein.data + 4*form.carbs.data + 9*form.fat.data

        current_user.macros[0].protein = form.protein.data
        current_user.macros[0].carbs = form.carbs.data
        current_user.macros[0].fat = form.fat.data
        current_user.macros[0].calories = calories

        db.session.commit()

        flash("You have set your daily macros.", "success")

        return redirect(url_for('nutrition'))

    return render_template('set-macros.html', title = "Set Macros", form = form)


#
@app.route("/nutrition/new-meal", methods = ['GET', 'POST'])
@login_required
def new_meal1():
    form = MealForm()

    if form.validate_on_submit():
        calories = 4*form.protein.data + 4*form.carbs.data + 9*form.fat.data

        meal = Meal(description = form.description.data, food_type = form.food_type.data, time = form.time.data, protein = form.protein.data,
            carbs = form.carbs.data, fat = form.fat.data, calories = calories, user_id = current_user.id)

        db.session.add(meal)
        db.session.commit()

        flash("You have successfully logged your meal.", "success")
        return redirect(url_for('nutrition'))

    return render_template('new-meal.html', title = "New Meal", form = form)


#
@app.route("/nutrition/meal-log/new-meal", methods = ['GET', 'POST'])
@login_required
def new_meal2():
    form = MealForm()

    if form.validate_on_submit():
        calories = 4*form.protein.data + 4*form.carbs.data + 9*form.fat.data

        meal = Meal(description = form.description.data, food_type = form.food_type.data, time = form.time.data, protein = form.protein.data,
            carbs = form.carbs.data, fat = form.fat.data, calories = calories, user_id = current_user.id)

        db.session.add(meal)
        db.session.commit()

        flash("You have successfully logged your meal.", "success")
        return redirect(url_for('meal_log'))

    return render_template('new-meal.html', title = "New Meal", form = form)


#
@app.route("/nutrition/meal-log")
@login_required
def meal_log():
    today = datetime.today()

    meals = Meal.query.filter(Meal.user_id == current_user.id).all()
    todays_meals = [x for x in meals if x.time.strftime('%d-%m-%Y') == today.strftime('%d-%m-%Y')]

    sorted_meals = sorted(todays_meals, key = operator.attrgetter('calories'))

    return render_template('meal-log.html', title = "Meal Log", meals = todays_meals, sorted_meals = sorted_meals,
        today = datetime.today())


#
@app.route("/nutrition/meal-log/<int:meal_id>/update-meal", methods = ['GET', 'POST'])
@login_required
def update_meal(meal_id):
    meal = Meal.query.filter(Meal.user_id == current_user.id, Meal.id == meal_id).first()

    if meal.user != current_user:
        abort(403)

    form = MealForm()

    if form.validate_on_submit():
        meal.description = form.description.data
        meal.food_type = form.food_type.data
        meal.time = form.time.data
        meal.protein = form.protein.data
        meal.carbs = form.carbs.data
        meal.fat = form.fat.data

        meal.calories = 4*form.protein.data + 4*form.carbs.data + 9*form.fat.data

        db.session.commit()

        return redirect(url_for('meal_log'))

    elif request.method == 'GET':
        form.description.data = meal.description
        form.food_type.data = meal.food_type
        form.time.data = meal.time
        form.protein.data = meal.protein
        form.carbs.data = meal.carbs
        form.fat.data = meal.fat

    return render_template('update-meal.html', title = "Edit Your Meal", form = form)


#
@app.route("/nutrition/meal-log/<int:meal_id>/delete-meal", methods = ['GET'])
@login_required
def delete_meal(meal_id):
    meal = Meal.query.filter(Meal.user_id == current_user.id, Meal.id == meal_id).first()

    if meal.user != current_user:
        abort(403)

    db.session.delete(meal)
    db.session.commit()

    flash("You have successfully deleted your meal.", "success")
    return redirect(url_for('meal_log'))


#
@app.route("/nutrition/nutrition-resources")
@login_required
def nutrition_resources():
    return render_template('nutr-res.html', title = "Nutrition Resources")



#
@app.route("/community")
def community():
    return render_template('community.html', title = 'Community')


#
def set_blank_schedule(user_id):
    schedule1 = Schedule(day_of_week = "Monday", workout = "None Set.", user_id = user_id)
    schedule2 = Schedule(day_of_week = "Tuesday", workout = "None Set.", user_id = user_id)
    schedule3 = Schedule(day_of_week = "Wednesday", workout = "None Set.", user_id = user_id)
    schedule4 = Schedule(day_of_week = "Thursday", workout = "None Set.", user_id = user_id)
    schedule5 = Schedule(day_of_week = "Friday", workout = "None Set.", user_id = user_id)
    schedule6 = Schedule(day_of_week = "Saturday", workout = "None Set.", user_id = user_id)
    schedule7 = Schedule(day_of_week = "Sunday", workout = "None Set.", user_id = user_id)

    db.session.add(schedule1)
    db.session.add(schedule2)
    db.session.add(schedule3)
    db.session.add(schedule4)
    db.session.add(schedule5)
    db.session.add(schedule6)
    db.session.add(schedule7)


#
@app.route("/profile-creation/<username>", methods = ['GET', 'POST'])
def profile_creation(username):
    form = ProfileForm()

    if form.validate_on_submit():

        username = flask.session['user']
        first_name = flask.session['first_name']
        last_name = flask.session['last_name']
        email = flask.session['email']
        password = flask.session['password']

        user = User(username = username, first_name = first_name, last_name = last_name, email = email,
            password = password)

        db.session.add(user)
        db.session.commit()

        user_id = user.id

        profile = Profile(weight = form.weight.data, height = form.height.data, goal = form.goal.data, age = form.age.data,
            gender = form.gender.data, location = form.location.data, quote = form.quote.data, user_id = user_id)

        macros = Macros(protein = -1, carbs = -1, fat = -1, calories = -1, user_id = user_id)

        db.session.add(macros)
        db.session.add(profile)
        set_blank_schedule(user_id)

        db.session.commit()

        login_user(user)

        flash(f'You have successfully created your account!', 'success')

        return redirect(url_for('fitness_page'))

    return render_template('profile-creation.html', title = "Create Your Profile", form = form)


#
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # user = User(username = form.username.data, first_name = form.first_name.data, last_name = form.last_name.data,
        #     email = form.email.data, password = hashed_password)

        flask.session['user'] = form.username.data
        flask.session['first_name'] = form.first_name.data
        flask.session['last_name'] = form.last_name.data
        flask.session['email'] = form.email.data
        flask.session['password'] = hashed_password

        username = form.username.data

        flash(f'Please set up your profile to create your account.', 'success')

        return redirect(url_for('profile_creation', username = username))

    return render_template('register.html', title = 'Register', form = form)


#
@app.route("/login", methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)

            #next_page = request.args.get('next')

            flash("You have successfully logged in.", "success")

            #return redirect(next_page) if next_page else redirect(url_for('fitness_page'))
            return redirect(url_for('fitness_page'))

        else:
            flash('Login Unsuccessful. Please check your username and/or password.', 'danger')

    return render_template('login.html', title = 'Log In', form = form)


#
@app.route("/logout")
def logout():
    logout_user()

    flash('You have successfully logged out.', 'success')

    return redirect(url_for('home'))


#
@app.route("/account")
@login_required
def account():
    image_file = url_for('static', filename = 'images/' + current_user.profile_image)

    return render_template('account.html', title = 'Your Account', image_file = image_file)


#
def save_picture(picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(picture.filename)

    picture_filename = random_hex + file_ext

    picture_path = os.path.join(app.root_path, 'static/images', picture_filename)

    output_size = (500, 500)
    i = Image.open(picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_filename


#
@app.route("/account/update-profile-picture", methods = ['GET', 'POST'])
@login_required
def change_profile_image():
    form = ChangeProfilePicForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)

            current_user.profile_image = picture_file

        db.session.commit()

        flash(f'You have successfully changed your profile picture.', 'success')

        return redirect(url_for('account'))

    return render_template('update-profile-picture.html', title = 'Update Profile Picture', form = form)



#
@app.route("/account/update-user-email", methods = ['GET', 'POST'])
@login_required
def change_user():
    form = ChangeUserForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()

        flash(f'You have successfully updated your username and email', 'success')

        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('update-user.html', title = 'Update Profile', form = form)


#
@app.route("/account/change-password", methods = ['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        new_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        current_user.password = new_pw

        db.session.commit()

        flash(f'You have successfully changed your password.', 'success')

        return redirect(url_for('account'))

    return render_template('change-password.html', title = 'Change Password', form = form)






