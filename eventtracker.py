from modules.sk import eventtrack, getranks
from apscheduler.schedulers.blocking import BlockingScheduler


scheduler = BlockingScheduler()
scheduler.add_job(getranks, 'cron', minute=10, id='getranks10')
scheduler.add_job(getranks, 'cron', minute=30, id='getranks30')
scheduler.add_job(getranks, 'cron', minute=50, id='getranks50')
scheduler.add_job(eventtrack, 'cron', second=0, id='chafang')
scheduler.start()