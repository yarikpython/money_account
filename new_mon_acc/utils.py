from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict
from new_mon_acc.models import User, History
from flask_login import current_user
import os
from new_mon_acc import app
import secrets
from datetime import datetime


def create_pie(dict):
    labels = []
    slices = []
    for item in dict.items():
        labels.append(f'{item[0]} {item[1]} BYN')
        slices.append(item[1])
    plt.style.use('fivethirtyeight')
    colors = ['#56e2cf', '#56aee2', '#5668e2', '#8a56e2', '#cf56e2', '#e256ae', '#e25668', '#e2cf56', '#e2cf56',
              '#aee256', '#68e256', '#56e289']
    plt.pie(slices, labels=labels, colors=colors, wedgeprops={'edgecolor': 'white'})
    plt.tight_layout()
    plt.title(f'My Latest Report {datetime.utcnow().strftime("%d.%m.%Y")}')
    filename = secrets.token_hex(8)
    path = os.path.join(app.root_path, 'static/', f'{filename}.png')
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    current_user.latest_report = f'{filename}.png'
    plt.close()
    return filename


def prepare_data(user_id, start_date, finish_date):
    user = User.query.get(user_id)
    output = defaultdict(int)
    for note in History.query.filter_by(user_id=user.id).filter(start_date <= History.date).filter(
            History.date <= finish_date).all():
        output[note.category.name] += note.spend
    return output
