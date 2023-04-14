import datetime
import os
import random

from flask import jsonify, url_for
from flask import Flask, render_template, redirect, request, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from flask_restful import abort, Api

from werkzeug.security import generate_password_hash

from data.forms.NoPictureForm import NoPictureForm
from data.forms.fabrics_form import FabricsForm
from data.forms.filter_form import FilterForm
from data.forms.simple_table_form import SimpleForm
from data.models.additional import Countries, Types
from data.models.fabrics import Fabrics
from data.models.user import User

from data.models import db_session
from data.models.wardrobe import Wardrobe
from data.resources import collars_resource, brims_resource, heels_resource, clasps_resource, \
    lapels_resource, sleeves_resource, patterns_resource, trouser_lengths_resource, \
    countries_resource, fits_resource, seasons_resource, sizes_resource, types_resource, \
    users_resource, \
    boots_resource, hats_resource, lower_body_resource, upper_body_resource, \
    fabrics_resource, wardrobe_resource

from data.constants.tables_inf import TABLES, TABLES_CLASSES, FIELDS, RELATIONS, NO_PICTURE, SIMPLE, TRANSLATION

from data.forms.login_in import LoginInForm
from data.forms.registration_form import RegisterForm

from data.maps import finder


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    for i in os.listdir(os.path.join('temp', "pictures")):
        if i != "information.txt":
            os.remove("temp/pictures/" + i)
    db_session.global_init("db/designer_base.db")
    # app.register_blueprint(users_api.blueprint)
    # app.register_blueprint(jobs_api.blueprint)

    # для списка объектов
    api.add_resource(collars_resource.CollarsListResource, '/api/collars')
    api.add_resource(brims_resource.BrimsListResource, '/api/brims')
    api.add_resource(clasps_resource.ClaspsListResource, '/api/clasps')
    api.add_resource(heels_resource.HeelsListResource, '/api/heels')
    api.add_resource(lapels_resource.LapelsListResource, '/api/lapels')
    api.add_resource(sleeves_resource.SleevesListResource, '/api/sleeves')
    api.add_resource(trouser_lengths_resource.TrouserLengthsListResource, '/api/trouserlengths')
    api.add_resource(patterns_resource.PatternsListResource, '/api/patterns')
    api.add_resource(users_resource.UsersListResource, '/api/users')
    api.add_resource(fits_resource.FitsListResource, '/api/fits')
    api.add_resource(seasons_resource.SeasonsListResource, '/api/seasons')
    api.add_resource(countries_resource.CountriesListResource, '/api/countries')
    api.add_resource(sizes_resource.SizesListResource, '/api/sizes')
    api.add_resource(types_resource.TypesListResource, '/api/types')
    api.add_resource(boots_resource.BootsListResource, '/api/boots')
    api.add_resource(hats_resource.HatsListResource, '/api/hats')
    api.add_resource(lower_body_resource.LowerBodyListResource, '/api/lower_body')
    api.add_resource(upper_body_resource.UpperBodyListResource, '/api/upper_body')
    api.add_resource(fabrics_resource.FabricsListResource, '/api/fabrics')
    api.add_resource(wardrobe_resource.WardrobeListResource, '/api/wardrobe')


    # для одного объекта
    api.add_resource(collars_resource.CollarsResource, '/api/collars/<int:collars_id>')
    api.add_resource(brims_resource.BrimsResource, '/api/brims/<int:brims_id>')
    api.add_resource(clasps_resource.ClaspsResource, '/api/clasps/<int:clasps_id>')
    api.add_resource(heels_resource.HeelsResource, '/api/heels/<int:heels_id>')
    api.add_resource(lapels_resource.LapelsResource, '/api/lapels/<int:lapels_id>')
    api.add_resource(sleeves_resource.SleevesResource, '/api/sleeves/<int:sleeves_id>')
    api.add_resource(trouser_lengths_resource.TrouserLengthsResource, '/api/trouserlengths/<int:trouserlengths_id>')
    api.add_resource(patterns_resource.PatternsResource, '/api/patterns/<int:patterns_id>')
    api.add_resource(users_resource.UsersResource, '/api/users/<int:users_id>')
    api.add_resource(countries_resource.CountriesResource, '/api/countries/<int:countries_id>')
    api.add_resource(fits_resource.FitsResource, '/api/fits/<int:fits_id>')
    api.add_resource(seasons_resource.SeasonsResource, '/api/seasons/<int:seasons_id>')
    api.add_resource(sizes_resource.SizesResource, '/api/sizes/<int:sizes_id>')
    api.add_resource(types_resource.TypesResource, '/api/types/<int:types_id>')
    api.add_resource(boots_resource.BootsResource, '/api/boots/<int:boots_id>')
    api.add_resource(hats_resource.HatsResource, '/api/hats/<int:hats_id>')
    api.add_resource(lower_body_resource.LowerBodyResource, '/api/lower_body/<int:lower_body_id>')
    api.add_resource(upper_body_resource.UpperBodyResource, '/api/upper_body/<int:upper_body_id>')
    api.add_resource(fabrics_resource.FabricsResource, '/api/fabrics/<int:fabrics_id>')
    api.add_resource(wardrobe_resource.WardrobeResource, '/api/wardrobe/<int:wardrobe_id>')

    app.run()


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    # if current_user.is_authenticated:
    #     jobs = db_sess.query(Jobs).filter((Jobs.user == current_user) | (Jobs.is_finished != True))
    # else:
    #     jobs = db_sess.query(Jobs).filter(Jobs.is_finished != True)
    return render_template("index.html", title="Designer help")


@app.route("/show/<table>/<int:id_>")
def element_information(table, id_):
    db_sess = db_session.create_session()
    if table not in TABLES:
        abort(404)
    obj = db_sess.query(TABLES_CLASSES[table]).filter(TABLES_CLASSES[table].id == id_).first()
    if not obj:
        abort(404)
    if table == "Wardrobe":
        if not current_user or not obj.owner == current_user.id and not current_user.access == 3:
            abort(403)
    if table == "users":
        if not current_user or current_user.access != 3:
            abort(403)
    fields = FIELDS[table]
    data = {}
    for i in fields:
        data[i] = getattr(obj, i)
    for i in fields:
        if i in RELATIONS:
            data[i] = db_sess.query(TABLES_CLASSES[RELATIONS[i]]).filter(TABLES_CLASSES[RELATIONS[i]].id ==
                                                                         data[i]).first()
    if table in ["Upper_body", "Lower_body", "Hats", "Boots"]:
        country = db_sess.query(Countries).filter(Countries.id == obj.origin).first()
        ll_span = finder.get_ll_span(country.name)
        coords = finder.get_coords(country.name)
        map_pic = finder.get_map(*ll_span, (str(coords[0]) + "," + str(coords[1]), "pm2bll"))
        random_int = random.randint(0, 1000000)
        with open(f"temp/pictures/map_picture{random_int}.png", "wb") as f:
            f.write(map_pic)
        data["map"] = url_for('temp', filename='pictures/map_picture{random_int}.png')
    return render_template("elem_information", title="Информация", data=data)


@app.route("/info/<int:id>")
@login_required
def info(id_):
    if current_user and current_user.id == id_:
        return redirect("/show/users/" + str(id_))
    abort(403)


@app.route("/wardrobe/<sort_str>", methods=['GET', 'POST'])
@login_required
def wardrobe(sort_str):
    form = FilterForm()
    if form.validate_on_submit():
        return redirect("/wardrobe/" + (request.form["sort_str"] if "sort_str" in request.form else ""))
    db_sess = db_session.create_session()
    results = db_sess.query(Wardrobe).filter((Wardrobe.owner == current_user.id) & (Wardrobe.deleted == 0)).all()
    data = []
    for obj in results:
        if sort_str in db_sess.get(TABLES_CLASSES[db_sess.get(Types, obj.type_).name], obj.id):
            fields = FIELDS["Wardrobe"]
            del fields[-1]
            data = {}
            for i in fields:
                data[i] = getattr(obj, i)
            for i in fields:
                if i in RELATIONS:
                    data[i] = db_sess.query(TABLES_CLASSES[RELATIONS[i]]).filter(TABLES_CLASSES[RELATIONS[i]].id ==
                                                                                 data[i]).first()
    return render_template("wardrobe.html", data=data, title="Гардероб", form=form)


@app.route("/additional/<type_>/<sort_str>", methods=['GET', 'POST'])
def additional(type_, sort_str):
    if not(type_ in NO_PICTURE or type_ in SIMPLE or type_ == "Fabrics"):
        abort(404)
    form = FilterForm()
    if form.validate_on_submit():
        return redirect(f"/additional/{type_}/" + (request.form["sort_str"] if "sort_str" in request.form else ""))
    db_sess = db_session.create_session()
    table = TABLES_CLASSES[type_]
    results = db_sess.query(table).filter((table.deleted == 0) & (table.name.like(f'%{sort_str}%'))).all()
    data = []
    for obj in results:
        fields = FIELDS[type_]
        del fields[-1]
        data = {}
        for i in fields:
            data[i] = getattr(obj, i)
    if type_ in NO_PICTURE:
        return render_template("no_picture.html", data=data, title=TRANSLATION[type_], form=form)
    elif type_ in SIMPLE:
        return render_template("simple.html", data=data, title=TRANSLATION[type_], form=form)
    else:
        return render_template("fabrics.html", data=data, title=TRANSLATION[type_], form=form)


@login_required
@app.route("/users/<sort_str>", methods=['GET', 'POST'])
def users(sort_str):
    if current_user.access != 3:
        abort(403)
    form = FilterForm()
    if form.validate_on_submit():
        return redirect(f"/users/" + (request.form["sort_str"] if "sort_str" in request.form else ""))
    db_sess = db_session.create_session()
    results = db_sess.query(User).filter((User.deleted == 0) & (User.name.like(f'%{sort_str}%'))).all()
    data = []
    for obj in results:
        fields = FIELDS["users"]
        del fields[-1]
        del fields[2]
        data = {}
        for i in fields:
            data[i] = getattr(obj, i)
    return render_template("users.html", data=data, title="Пользователи", form=form)


@app.route("/clothes/<type_>/<sort_str>", methods=['GET', 'POST'])
def clothes(type_, sort_str):
    if type_ not in ["Boots", "Hats", "Lower_body", "Upper_body"]:
        abort(404)
    form = FilterForm()
    if form.validate_on_submit():
        return redirect(f"/clothes/{type_}/" + (request.form["sort_str"] if "sort_str" in request.form else ""))
    table = TABLES_CLASSES[type_]
    db_sess = db_session.create_session()
    results = db_sess.query(table).filter((table.deleted == 0) & (table.name.like(f'%{sort_str}%'))).all()
    data = []
    for obj in results:
        fields = FIELDS[type_]
        del fields[-1]
        data = {}
        for i in fields:
            data[i] = getattr(obj, i)
            if i in RELATIONS:
                data[i] = db_sess.query(TABLES_CLASSES[RELATIONS[i]]).filter(TABLES_CLASSES[RELATIONS[i]].id ==
                                                                             data[i]).first()
    if type_ == "Boots":
        return render_template("boots.html", data=data, title="Обувь", form=form)
    elif type_ == "Hats":
        return render_template("hats.html", data=data, title="Шляпы", form=form)
    elif type_ == "Upper_body":
        return render_template("upper_body.html", data=data, title="Верхняя одежда", form=form)
    return render_template("lower_body.html", data=data, title="Нижняя одежда", form=form)


@app.route("/additional/add/<type_>", methods=['GET', 'POST'])
@login_required
def additional_add(type_):
    if current_user.access < 2:
        abort(403)
    db_sess = db_session.create_session()
    if type_ in SIMPLE:
        form = SimpleForm()
        if form.validate_on_submit():
            obj = TABLES_CLASSES[type_]
            obj.name = form.name.data
            if not os.path.exists(os.path.join("static", type_.lower())):
                os.mkdir(os.path.join("static", type_.lower()))
            where = "pic_" + obj.name
            if os.path.exists(os.path.join("static/img", type_.lower() + "/pic_" + obj.name)):
                i = 1
                while os.path.exists(os.path.join("static/img", type_.lower() + "/pic_" + obj.name + str(i))):
                    i += 1
                    where = "/pic_" + obj.name + str(i)
            with open(where, "wb") as f:
                f.write(form.picture.data)
            obj.picture = where
            db_sess.add(obj)
            db_sess.commit()
            return redirect('/additional/' + type_)
        render_template("simple_add.html", form=form, title="Добавить " + TRANSLATION[type_])
    elif type_ in NO_PICTURE:
        form = NoPictureForm()
        if form.validate_on_submit():
            obj = TABLES_CLASSES[type_]
            obj.name = form.name.data
            db_sess.add(obj)
            db_sess.commit()
            return redirect('/additional/' + type_)
        render_template("no_picture_add.html", form=form, title="Добавить " + TRANSLATION[type_])
    elif type_ == "Fabrics":
        form = FabricsForm()
        if form.validate_on_submit():
            obj = TABLES_CLASSES[type_]
            obj.name = form.name.data
            obj.warmth = form.warmth.data
            obj.washing = form.washing.data
            if not os.path.exists(os.path.join("static", type_.lower())):
                os.mkdir(os.path.join("static", type_.lower()))
            where = "pic_" + obj.name
            if os.path.exists(os.path.join("static/img", type_.lower() + "/pic_" + obj.name)):
                i = 1
                while os.path.exists(os.path.join("static/img", type_.lower() + "/pic_" + obj.name + str(i))):
                    i += 1
                    where = "/pic_" + obj.name + str(i)
            with open(where, "wb") as f:
                f.write(form.picture.data)
            obj.picture = where
            db_sess.add(obj)
            db_sess.commit()
            return redirect('/additional/' + type_)
        render_template("fabrics_add.html", form=form, title="Добавить " + TRANSLATION[type_])
    abort(404)


@app.route("/wardrobe/<int:id_>")
@login_required
def wardrobe_del(id_):
    db_sess = db_session.create_session()
    obj = db_sess.get(Wardrobe, id_)
    if not obj:
        abort(404)
    if obj.owner != current_user.id and not current_user.access == 3:
        abort(403)
    db_sess.delete(obj)
    db_sess.commit()


@app.route("/clothes/<type_>/<int:id_>")
@login_required
def clothes_del(type_, id_):
    db_sess = db_session.create_session()
    if type_ not in ["Boots", "Hats", "Lower_body", "Upper_body"]:
        abort(404)
    obj = db_sess.get(TABLES_CLASSES[type_], id_)
    if not obj:
        abort(404)
    if not current_user.access >= 2:
        abort(403)
    db_sess.delete(obj)
    db_sess.commit()


@app.route("/additional/<type_>/<int:id_>")
@login_required
def additional_del(type_, id_):
    db_sess = db_session.create_session()
    if not(type_ in NO_PICTURE or type_ in SIMPLE or type_ == "Fabrics"):
        abort(404)
    obj = db_sess.get(TABLES_CLASSES[type_], id_)
    if not obj:
        abort(404)
    if not current_user.access >= 2:
        abort(403)
    db_sess.delete(obj)
    db_sess.commit()


@app.route("/users/<int:id_>")
@login_required
def users_del(id_):
    db_sess = db_session.create_session()
    obj = db_sess.get(User, id_)
    if not obj:
        abort(404)
    if not current_user.access == 3:
        abort(403)
    db_sess.delete(obj)
    db_sess.commit()


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginInForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # print(form.password.data)
        # если вам скучно, то разкомментируйте эту^ строку
        # запустите сервер и отправьте ссылку в классный чат с просьбой потестить
        # 100% кто-нибудь зарегистрируется с настоящими почтой и паролем (уже такое было)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login_in.html',
                               message="Неправильный логин или пароль",
                               form=form, title="Неудача")
    return render_template('login_in.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        ans = {"name": "", "email": "", "password": ""}
        for i in ans:
            if i in request.form:
                ans[i] = request.form[i]
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('used_email.html')  # если пытаться зарегистрироваться с почтой, которая уже есть
        user = User()
        user.name = ans["name"]
        user.email = ans["email"]
        user.hashed_password = generate_password_hash(ans["password"])
        # print([ans["password"]], user.hashed_password, generate_password_hash(ans["password"]))
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect("/")
    return render_template('user_form.html', title='Регистрация', form=form)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request 400'}), 400)


@app.errorhandler(403)
def access_denied(_):
    return make_response(jsonify({'error': 'Access denied 403'}), 403)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found 404'}), 404)


@app.errorhandler(405)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request 405'}), 405)


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
