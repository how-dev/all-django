from apscheduler.schedulers.background import BackgroundScheduler


def start(view):
    scheduler = BackgroundScheduler()
    views = view()

    scheduler.add_job(
        views.scheduler,
        "interval",
        replace_existing=True,
        **views.scheduler_time,
    )

    scheduler.start()
