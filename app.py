from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import boto3

app = Flask(__name__)

# SQLAlchemy 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:It12345!@team3-db-01-instance-1.c1eiqtt31v98.ap-northeast-2.rds.amazonaws.com:3306/recapark'
db = SQLAlchemy(app)

# 모델 클래스 정의
class Ticket(db.Model):
    __tablename__ = 'new_ticket_table'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


db.reflect()

@app.route('/')
def index():
    return render_template('index.html', tickets=Ticket.query.all())


sqs = boto3.client('sqs', region_name='ap-northeast-2')

@app.route('/buy/<int:ticket_id>', methods=['GET', 'POST'])
def buy(ticket_id):
    if request.method == 'POST':
        ticket = Ticket.query.get(ticket_id)

        if ticket and ticket.quantity > 0:
            purchased_quantity = int(request.form['quantity'])
            if purchased_quantity <= ticket.quantity:
                # 여기에서 실제 구매 로직을 추가할 수 있습니다.
                # 예시로 구매 내용을 SQS로 전송합니다.
                purchase_data = {
                    'ticket_id': ticket_id,
                    'event': ticket.event,
                    'price': ticket.price,
                    'quantity': purchased_quantity,
                    'total_price': ticket.price * purchased_quantity
                }

                # SQS에 메시지 전송
                sqs.send_message(
                    QueueUrl='https://sqs.ap-northeast-2.amazonaws.com/447079561480/Ticket-Buy-Queue.fifo',
                    MessageBody=json.dumps(purchase_data)
                )

                # 티켓 수량 갱신
                ticket.quantity -= purchased_quantity
                db.session.commit()

                return redirect(url_for('index'))
    else:
        ticket = Ticket.query.get(ticket_id)
        if ticket:
            return render_template('buy.html', ticket=ticket)
        else:
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)