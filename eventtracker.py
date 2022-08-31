from modules.sk import eventtrack, getranks
from apscheduler.schedulers.blocking import BlockingScheduler


getranks()
eventtrack()
scheduler = BlockingScheduler()
scheduler.add_job(getranks, 'interval', minutes=20, id='getranks')
scheduler.add_job(eventtrack, 'interval', seconds=60, id='chafang')
scheduler.start()