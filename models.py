from datetime import datetime
from app import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    responsible = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    # Relationship with progress updates
    progress_updates = db.relationship('ProgressUpdate', backref='task', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and not self.completed:
            return self.due_date < datetime.now().date()
        return False
    
    @property
    def status_class(self):
        """Return CSS class based on task status"""
        if self.completed:
            return 'task-completed'
        elif self.is_overdue:
            return 'task-overdue'
        else:
            return 'task-pending'
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage based on number of updates"""
        if self.completed:
            return 100
        
        # Count progress updates for this task
        from sqlalchemy import func
        from app import db
        update_count = db.session.query(func.count(ProgressUpdate.id)).filter_by(task_id=self.id).scalar() or 0
        
        if update_count == 0:
            return 0
        else:
            # Simple calculation: each update adds some progress
            # Can be customized later for more sophisticated tracking
            return min(80, update_count * 20)

class ProgressUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ProgressUpdate {self.id} for Task {self.task_id}>'
