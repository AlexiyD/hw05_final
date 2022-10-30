import datetime as dtime


def year(request):

    year = dtime.datetime.now().strftime('%Y')
    return {
        'year': int(year),
    }
