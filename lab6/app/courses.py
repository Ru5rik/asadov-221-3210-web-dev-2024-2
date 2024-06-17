from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from models import db, Course, Category, User, Review
from tools import CoursesFilter, ImageSaver, ReviewFilter

bp = Blueprint('courses', __name__, url_prefix='/courses')

COURSE_PARAMS = [
    'author_id', 'name', 'category_id', 'short_desc', 'full_desc'
]


def params():
    return {p: request.form.get(p) or None for p in COURSE_PARAMS}
    

def review_params():
    return {
        'text': request.form.get('text'),
        'raiting': request.form.get('raiting'),
    }


def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': [x for x in request.args.getlist('category_ids') if x],
    }

def search_review_params():
    return {
        'review_types': request.args.get('review_types')
    }

@bp.route('/')
def index():
    courses = CoursesFilter(**search_params()).perform()
    pagination = db.paginate(courses)
    courses = pagination.items
    categories = db.session.execute(db.select(Category)).scalars()
    return render_template('courses/index.html',
                           courses=courses,
                           categories=categories,
                           pagination=pagination,
                           search_params=search_params())


@bp.route('/new')
@login_required
def new():
    course = Course()
    categories = db.session.execute(db.select(Category)).scalars()
    users = db.session.execute(db.select(User)).scalars()
    return render_template('courses/new.html',
                           categories=categories,
                           users=users,
                           course=course)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    f = request.files.get('background_img')
    img = None
    course = Course()
    try:
        if f and f.filename:
            img = ImageSaver(f).save()

        image_id = img.id if img else None
        course = Course(**params(), background_image_id=image_id)
        db.session.add(course)
        db.session.commit()
    except IntegrityError as err:
        flash(
            f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        db.session.rollback()
        categories = db.session.execute(db.select(Category)).scalars()
        users = db.session.execute(db.select(User)).scalars()
        return render_template('courses/new.html',
                            categories=categories,
                            users=users,
                            course=course)

    flash(f'Курс {course.name} был успешно добавлен!', 'success')

    return redirect(url_for('courses.index'))


@bp.route('/<int:course_id>/')
def show(course_id):
    course = db.get_or_404(Course, course_id)
    query = db.select(Review).where(Review.course_id == course_id).order_by(Review.created_at.desc()).limit(5)
    reviews = db.session.scalars(query)
    reviews = {} if reviews is None else reviews

    query = db.select(Review).where(Review.user_id == current_user.id)
    can = False if db.session.scalar(query) else True
    return render_template('courses/show.html', course=course, reviews=reviews, can=can)

@bp.route('/<int:course_id>/comment', methods=['POST'])
@login_required
def comment(course_id):
    try:
        review = Review(**review_params())
        if review.text is None or len(review.text) == 0:
            flash(f'Заполните форму!', 'warning')
            return redirect(url_for('courses.show', course_id=course_id))
        review.course_id = course_id
        review.user_id = current_user.id

        course = db.get_or_404(Course, course_id)


        print(db.session.query(Review).filter(Review.user_id == current_user.id, Review.course_id == course_id).all())
        can =  db.session.query(Review).filter(Review.user_id == current_user.id, Review.course_id == course_id).all() or False
        if can:
            flash(f'У вас уже есть отзыв!', 'warning')
            return redirect(url_for('courses.show', course_id=course_id))

        course.rating_num = course.rating_num + 1
        course.rating_sum = course.rating_sum + int(review.raiting)

        db.session.add(review)
        db.session.add(course)
        db.session.commit()
    except IntegrityError as err:
        flash(f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        db.session.rollback()
    flash(f'Отзыв был успешно добавлен!', 'success')
    return redirect(url_for('courses.show', course_id=course_id))
        
@bp.route('/<int:course_id>/reviews')
def reviews(course_id):
    resparams = {}
    resparams = search_review_params()
    resparams['course_id'] = course_id
    reviews = ReviewFilter(**resparams).perform()

    pagination = db.paginate(reviews, per_page=5)
    
    reviews = pagination.items
    return render_template('courses/reviews.html',
                           reviews=reviews,
                           pagination=pagination,
                           params=resparams)
                        #    search_params=search_review_params(),
                        #    params={'course_id': course_id})