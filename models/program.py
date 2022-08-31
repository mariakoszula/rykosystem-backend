from db import db
from models.base_database_query import BaseDatabaseQuery
from helpers import DataConverter

class ProgramModel(db.Model, BaseDatabaseQuery):
    __tablename__ = 'program'

    id = db.Column(db.Integer, primary_key=True)
    semester_no = db.Column(db.Integer, nullable=False)
    school_year = db.Column(db.String(20), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    fruitVeg_price = db.Column(db.Float)
    dairy_price = db.Column(db.Float)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    dairy_min_per_week = db.Column(db.Integer)
    fruitVeg_min_per_week = db.Column(db.Integer)
    dairy_amount = db.Column(db.Integer)
    fruitVeg_amount = db.Column(db.Integer)

    company = db.relationship('CompanyModel')

    db.UniqueConstraint('school_year', 'semester_no')

    def __init__(self, semester_no, school_year, company_id, fruitVeg_price=0, dairy_price=0,
                 start_date=None, end_date=None, dairy_min_per_week=0, fruitVeg_min_per_week=0,
                 dairy_amount=0, fruitVeg_amount=0):
        self.fruitVeg_amount = fruitVeg_amount
        self.dairy_amount = dairy_amount
        self.fruitVeg_min_per_week = fruitVeg_min_per_week
        self.dairy_min_per_week = dairy_min_per_week
        self.end_date = end_date
        self.start_date = start_date
        self.semester_no = semester_no
        self.school_year = school_year
        self.company_id = company_id
        self.fruitVeg_price = fruitVeg_price
        self.dairy_price = dairy_price

    def __repr__(self):
        return f"Program: {self.id} semester_no:{self.semester_no} year:{self.school_year}"

    @classmethod
    def find(cls, school_year, semester_no):
        return cls.query.filter_by(semester_no=semester_no, school_year=school_year).first()

    def json(self):
        data: {} = super().json()
        DataConverter.replace_date_to_converted(data, "start_date")
        DataConverter.replace_date_to_converted(data, "end_date")
        return data
