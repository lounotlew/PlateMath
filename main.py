from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

#
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


#
@app.route("/about")
def about():
    return render_template('about.html', title = 'About')


#
@app.route("/my-fitness-page")
def fitness_page():
    return render_template('fitness-page-user.html', title = 'My Fitness Page')


#
@app.route("/workouts")
def workouts():
    return render_template('workouts-user.html', title = 'Workouts')


#
@app.route("/nutrition")
def nutrition():
    return render_template('nutrition-user.html', title = 'Nutrition')


#
@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        flash(f'Account successfully created for {form.username.data}!', 'success')

        return redirect(url_for('fitness_page'))

    return render_template('register.html', title = 'Register', form = form)


#
@app.route("/login")
def login():
    return


if __name__ == '__main__':
    app.run(debug = True)

