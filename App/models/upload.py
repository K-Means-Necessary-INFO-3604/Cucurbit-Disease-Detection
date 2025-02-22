from App.database import db

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    disease_type = db.Column(db.String(80), nullable=True)
    severity = db.Column(db.FLOAT, nullable=True)
    actions = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __init__(self, image, date, user_id=None, disease_type="undefined", severity=0.00, actions="undefined"):
        self.image = image
        self.date = date
        self.user_id = user_id
        self.disease_type = disease_type
        self.severity = severity
        self.actions = actions

    def get_json(self):
        return{
            'id': self.id,
            'date' : self.date,
            'user_id' : self.user_id,
            'type': self.disease_type,
            'severity': self.severity,
            'actions' : self.actions,
        }
