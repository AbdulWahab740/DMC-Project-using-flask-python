from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/DMC_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "secret_key" 
db = SQLAlchemy(app)

class StudentData(db.Model):
    __tablename__ = 'student_data'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    applicant = db.Column(db.String(50), nullable=False)
    father = db.Column(db.String(50), nullable=False)
    present_address = db.Column(db.String(100), nullable=False)
    permanent_address = db.Column(db.String(100), nullable=False)
    CNIC = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    regd = db.Column(db.String(20), nullable=False)
    challan = db.Column(db.String(20), nullable=False)
    degree = db.Column(db.String(20), nullable=False)
    faculty = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(20), nullable=False)
    passingYear = db.Column(db.String(20), nullable=False)
    marksObtained = db.Column(db.String(20), nullable=False)
    cgpa = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    Lib_status = db.Column(db.String(20), default='pending')
    adv_status = db.Column(db.String(20), default='pending')
    dsa_status = db.Column(db.String(20), default='pending')
    dean_status = db.Column(db.String(20), default='pending')
    def __repr__(self):
        return f"<Student {self.applicant}>"

class Signup(db.Model):
    __tablename__ = 'signup'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)  

    def __init__(self,email,password,username):
        self.email = email
        self.username = username
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def checkPassword(self, password):
        return bcrypt.checkpw(password.encode("utf-8"),self.password.encode("utf-8"))    
    
    def __repr__(self):
        return f"<Signup {self.email}>"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        Email = request.form["email"]
        password = request.form["password"]
        new_user = Signup.query.filter_by(email=Email).first()
        print(Email=="librarian@gmail.com" and password == "librarian")
        if Email=="librarian@gmail.com" and password == "librarian":
            return redirect(url_for("librarian"))
        
        elif Email=="advisor@gmail.com" and password == "advisor":
            return redirect(url_for("advisor"))
        
        elif Email=="dsa@gmail.com" and password == "dsa":
            return redirect(url_for("dsa"))
        
        elif Email=="dean@gmail.com" and password == "dean":
            return redirect(url_for("dean"))

        elif new_user and new_user.checkPassword(password):
            session['email'] = new_user.email
            print(session['email'])
            flash('Login successful!', 'success')
            return redirect(url_for('student'))
        
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template("index.html",error="Invalid User")
    return render_template("index.html")

@app.route("/librarian",methods=['GET','POST'])
def librarian():
    pending_students = StudentData.query.filter_by(Lib_status='pending').all()
    emails = Signup.query.with_entities(Signup.email).all()
    email_list = [email.email for email in emails]
    return render_template("librarian.html", students=pending_students)

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        
        new_user = Signup(email=email, username=username, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! You can now log in.', 'success')
            return redirect(url_for('student'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template("signup.html")

@app.route("/student", methods=["POST", "GET"])
def student():
    if request.method == "POST":
        # Extract form data
        applicant = request.form["applicant"]
        father = request.form["father"]
        present_address = request.form["present_address"]
        permanent_address = request.form["permanent_address"]
        CNIC = request.form["CNIC"]
        email = request.form["email"]
        regd = request.form["regd"]
        challan = request.form["challan"]
        degree = request.form["degree"]
        faculty = request.form["faculty"]
        section = request.form["section"]
        passingYear = request.form["passingYear"]
        marksObtained = request.form["marksObtained"]
        cgpa = request.form["cgpa"]
        

        # Create a new student object and add it to the database session
        new_student = StudentData(applicant=applicant, father=father, present_address=present_address,
                                  permanent_address=permanent_address, CNIC=CNIC, email=email,
                                  regd=regd, challan=challan,degree=degree,faculty=faculty,
                                  section=section,passingYear=passingYear,marksObtained=marksObtained,cgpa=cgpa)
        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Student data submitted successfully!', 'success')
            return redirect(url_for("Lib_status"))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template("student.html")

@app.route("/lib_approve/<int:id>", methods=["POST"])
def lib_approve(id):
    student = StudentData.query.get_or_404(id)
    student.Lib_status = "Approved "
    db.session.commit()
    flash('Request approved!', 'success')
    return redirect(url_for('librarian'))

@app.route("/lib_reject/<int:id>", methods=["POST"])
def lib_reject(id):
    student = StudentData.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Request rejected and removed!', 'success')
    return redirect(url_for('librarian'))

@app.route("/Lib_status", methods=["GET", "POST"])
def Lib_status():
    if request.method == "POST":
        email = request.form["email"]
        student = StudentData.query.filter_by(email=email).first()
        if student:
            return render_template("status_update.html", student=student)
        else:
            flash('No submission found for this email!', 'danger')
    return render_template("Lib_status.html")

##### Advisor Status

@app.route("/advisor",methods=['GET','POST'])
def advisor():
    pending_students = StudentData.query.filter_by(Lib_status='Approved', adv_status='pending').all()
    return render_template("advisor.html", students=pending_students)

@app.route("/adv_approve/<int:id>", methods=["POST"])
def adv_approve(id):
        student = StudentData.query.get_or_404(id)
        student.adv_status = "Approved "
        db.session.commit()
        flash('Request approved!', 'success')
        return redirect(url_for('advisor'))
            
@app.route("/adv_reject/<int:id>", methods=["POST"])
def adv_reject(id):
    student = StudentData.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Request rejected and removed!', 'success')
    return redirect(url_for('advisor'))

@app.route("/Lib_status", methods=["GET", "POST"])
def adv_status():
    if request.method == "POST":
        email = request.form["email"]
        student = StudentData.query.filter_by(email=email).first()
        if student:
            return render_template("status_update.html", student=student)
        else:
            flash('No submission found for this email!', 'danger')
    return render_template("Lib_status.html")

##### DSA Status
@app.route("/dsa",methods=['GET','POST'])
def dsa():
    # student = StudentData.query.filter_by(email=email).first()
    pending_students = StudentData.query.filter_by(adv_status='Approved', dsa_status='pending').all()
    print(pending_students)
    return render_template("dsa.html", students=pending_students)

@app.route("/dsa_approve/<int:id>", methods=["POST"])
def dsa_approve(id):
        print(id)
        student = StudentData.query.get_or_404(id)
        student.dsa_status = "Approved "
        print(student)
        db.session.commit()
        flash('Request approved!', 'success')
        return redirect(url_for('dsa'))
         
@app.route("/dsa_reject/<int:id>", methods=["POST"])
def dsa_reject(id):
    student = StudentData.query.get_or_404(id)
    print(student)
    db.session.delete(student)
    db.session.commit()
    flash('Request rejected and removed!', 'success')
    return redirect(url_for('dsa'))

@app.route("/Lib_status", methods=["GET", "POST"])
def dsa_status():
    if request.method == "POST":
        email = request.form["email"]
        student = StudentData.query.filter_by(email=email).first()
        if student:
            return render_template("status_update.html", student=student)
        else:
            flash('No submission found for this email!', 'danger')
    return render_template("Lib_status.html")

##### Dean Status
@app.route("/dean",methods=['GET','POST'])
def dean():
    # student = StudentData.query.filter_by(email=email).first()
    pending_students = StudentData.query.filter_by(dsa_status='Approved', dean_status='pending').all()
    return render_template("dean.html", students=pending_students)
    
@app.route("/dean_approve/<int:id>", methods=["POST"])
def dean_approve(id):
        student = StudentData.query.get_or_404(id)
        student.dean_status = "Approved "
        db.session.commit()
        flash('Request approved!', 'success')
        return redirect(url_for('dean'))
            
@app.route("/dean_reject/<int:id>", methods=["POST"])
def dean_reject(id):
    student = StudentData.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Request rejected and removed!', 'success')
    return redirect(url_for('dean'))

@app.route("/Lib_status", methods=["GET", "POST"])
def dean_status():
    if request.method == "POST":
        email = request.form["email"]
        student = StudentData.query.filter_by(email=email).first()
        if student:
            return render_template("status_update.html", student=student)
        else:
            flash('No submission found for this email!', 'danger')
    return render_template("Lib_status.html")

if __name__ == "__main__":
    app.run(debug=True)