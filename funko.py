# item.py - item functionality
from flask import Blueprint, render_template, request, redirect, session

# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column
from sqlalchemy import ForeignKey
from auth import get_current_user


# Base that adds dataclass behaviors to mapped classes
class Base(MappedAsDataclass, DeclarativeBase):
    pass


item_bp = Blueprint('item', __name__)
db = SQLAlchemy(model_class=Base)

class Series(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False, unique=True)

    def __repr__(self): # When you try to print or put this object in a template represent it as it's name
        return self.name


class Item(db.Model):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    task: Mapped[str] = mapped_column(db.String(200), nullable=False)
    user_id: Mapped[str] = mapped_column(db.String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)
    done: Mapped[bool] = mapped_column(db.Boolean, default=False)

    @property # item.category is a property (member variable) of the item object
    def category(self): # return the category object linked to this item by category_id
        return Series.query.get(self.category_id)
    
@item_bp.route('/')
def home():
    user = get_current_user()
    if not user:
        return render_template('login.html')
    session['user_id'] = user["id"]
    items = Item.query.filter_by(user_id=session['user_id']).all()
    categories = Series.query.all()
    return render_template('index.html', items=items, categories=categories, user=user)

@item_bp.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect('/')
    task_text = request.form['task']
    category_id = request.form.get('category_id', type=int)
    if not category_id:
        return redirect('/')
    new_task = Item(task=task_text, category_id=category_id, user_id=session['user_id'])
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')


@item_bp.route('/toggle/<int:item_id>')
def toggle(item_id):
    item = Item.query.get(item_id)
    if item and item.user_id == session['user_id']:
        item.done = not item.done
        db.session.commit()
    return redirect('/')


@item_bp.route('/delete/<int:item_id>')
def delete(item_id):
    item = Item.query.get(item_id)
    if item and item.user_id == session['user_id']:
        db.session.delete(item)
        db.session.commit()
    return redirect('/')


def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Seed initial categories if they don't exist
        if Series.query.count() == 0:
            urgent = Series(name="Urgent")
            non_urgent = Series(name="Non-urgent")
            db.session.add(urgent)
            db.session.add(non_urgent)
            db.session.commit()

        if Item.query.count() == 0:
            mreggleton_check = Item(task="Mr Eggleton checking your item App!", done=False, user_id="github|5987806", category_id=non_urgent.id)
            db.session.add(mreggleton_check)
            db.session.commit()